"""Live macro data service for deterministic validation scoring.

Policy:
- US locations -> FRED
- Non-US locations -> World Bank
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx


class MacroDataService:
    """Fetch and normalize macro indicators from public data APIs."""

    @staticmethod
    def _clip(v: float, lo: float = 0, hi: float = 100) -> int:
        return max(int(lo), min(int(hi), int(round(v))))

    @staticmethod
    def _norm_higher_better(x: float, low: float, high: float) -> int:
        if high <= low:
            return 50
        return MacroDataService._clip(100 * (x - low) / (high - low))

    @staticmethod
    def _norm_lower_better(x: float, low: float, high: float) -> int:
        if high <= low:
            return 50
        return MacroDataService._clip(100 * (high - x) / (high - low))

    @staticmethod
    def _location_tokens(location: str) -> set[str]:
        raw = (location or "").strip().lower().replace(",", " ")
        parts = [p for p in raw.split() if p]
        return set(parts)

    @staticmethod
    def _resolve_country(location: str) -> str:
        tokens = MacroDataService._location_tokens(location)
        raw = (location or "").strip().lower()

        us_terms = {
            "us", "usa", "u.s.", "u.s.a", "america", "united states", "united states of america"
        }
        if raw in us_terms or any(t in tokens for t in {"usa", "us", "texas", "california", "florida", "new", "york"}):
            return "US"

        uk_terms = {
            "uk", "u.k.", "united kingdom", "england", "scotland", "wales", "london", "manchester"
        }
        if raw in uk_terms or any(t in tokens for t in {"uk", "england", "scotland", "wales", "london"}):
            return "GB"

        # Common aliases
        if "nigeria" in tokens:
            return "NG"
        if "canada" in tokens:
            return "CA"

        if len(raw) == 2 and raw.isalpha():
            return raw.upper()
        return "GLOBAL"

    @staticmethod
    async def _fred_latest(client: httpx.AsyncClient, series_id: str, api_key: str) -> Optional[float]:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 12,
        }
        r = await client.get(url, params=params, timeout=8.0)
        r.raise_for_status()
        data = r.json()
        obs = data.get("observations", [])
        for row in obs:
            val = row.get("value")
            if val and val != ".":
                try:
                    return float(val)
                except Exception:
                    continue
        return None

    @staticmethod
    async def _world_bank_latest(client: httpx.AsyncClient, country: str, indicator: str) -> Optional[float]:
        # World Bank API: /country/{country}/indicator/{indicator}?format=json&per_page=60
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
        params = {"format": "json", "per_page": 60}
        r = await client.get(url, params=params, timeout=8.0)
        r.raise_for_status()
        payload = r.json()
        if not isinstance(payload, list) or len(payload) < 2:
            return None
        rows = payload[1] or []
        for row in rows:
            val = row.get("value")
            if val is not None:
                try:
                    return float(val)
                except Exception:
                    continue
        return None

    @staticmethod
    async def get_macro_profile(target_location: str) -> Dict[str, Any]:
        """Get normalized macro score from FRED (US) or World Bank (non-US)."""
        country = MacroDataService._resolve_country(target_location)
        now = datetime.now(timezone.utc).isoformat()

        # Sensible neutral defaults if API unavailable
        gdp_growth = 2.0
        inflation = 5.0
        unemployment = 6.0
        policy_rate = 6.0
        source = "fallback_defaults"
        indicators: Dict[str, Any] = {}

        try:
            async with httpx.AsyncClient() as client:
                if country == "US" and os.environ.get("FRED_API_KEY"):
                    api_key = os.environ.get("FRED_API_KEY", "")
                    gdp_growth = await MacroDataService._fred_latest(client, "A191RL1Q225SBEA", api_key) or gdp_growth
                    inflation = await MacroDataService._fred_latest(client, "CPIAUCSL", api_key) or inflation
                    unemployment = await MacroDataService._fred_latest(client, "UNRATE", api_key) or unemployment
                    policy_rate = await MacroDataService._fred_latest(client, "FEDFUNDS", api_key) or policy_rate
                    source = "fred"
                    indicators = {
                        "gdpGrowth": {"series": "A191RL1Q225SBEA", "value": gdp_growth},
                        "inflationProxy": {"series": "CPIAUCSL", "value": inflation},
                        "unemployment": {"series": "UNRATE", "value": unemployment},
                        "policyRate": {"series": "FEDFUNDS", "value": policy_rate},
                    }
                elif country not in {"GLOBAL", "US"}:
                    gdp_growth = await MacroDataService._world_bank_latest(client, country, "NY.GDP.MKTP.KD.ZG") or gdp_growth
                    inflation = await MacroDataService._world_bank_latest(client, country, "FP.CPI.TOTL.ZG") or inflation
                    unemployment = await MacroDataService._world_bank_latest(client, country, "SL.UEM.TOTL.ZS") or unemployment
                    policy_rate = await MacroDataService._world_bank_latest(client, country, "FR.INR.LEND") or policy_rate
                    source = "world_bank"
                    indicators = {
                        "gdpGrowth": {"indicator": "NY.GDP.MKTP.KD.ZG", "value": gdp_growth},
                        "inflation": {"indicator": "FP.CPI.TOTL.ZG", "value": inflation},
                        "unemployment": {"indicator": "SL.UEM.TOTL.ZS", "value": unemployment},
                        "policyRate": {"indicator": "FR.INR.LEND", "value": policy_rate},
                    }
        except Exception:
            # Keep fallback defaults and continue deterministic scoring.
            pass

        # Normalize to 0-100
        # Inflation / unemployment / rate: lower is better.
        # GDP growth: higher is better.
        gdp_n = MacroDataService._norm_higher_better(gdp_growth, -10, 10)
        infl_n = MacroDataService._norm_lower_better(inflation, 0, 20)
        unemp_n = MacroDataService._norm_lower_better(unemployment, 2, 25)
        rate_n = MacroDataService._norm_lower_better(policy_rate, 0, 25)

        macro_score = MacroDataService._clip(
            gdp_n * 0.30 + infl_n * 0.30 + unemp_n * 0.25 + rate_n * 0.15
        )

        return {
            "source": source,
            "country": country,
            "targetLocation": target_location,
            "updatedAt": now,
            "weights": {
                "gdpGrowth": 0.30,
                "inflation": 0.30,
                "unemployment": 0.25,
                "policyRate": 0.15,
            },
            "raw": {
                "gdpGrowth": gdp_growth,
                "inflation": inflation,
                "unemployment": unemployment,
                "policyRate": policy_rate,
            },
            "normalized": {
                "gdpGrowth": gdp_n,
                "inflation": infl_n,
                "unemployment": unemp_n,
                "policyRate": rate_n,
            },
            "score": macro_score,
            "indicators": indicators,
        }

