"""Deterministic market context service for validation scoring.

This service maps user-selected service context (serviceType/industry/location/market)
to normalized market factors. It does not use AI to score.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any


class MarketDataService:
    """Resolve market factors from selected service context."""

    _INDUSTRY_BASELINES = {
        "fintech": {"demand": 72, "competition": 80, "cpcPressure": 78, "macro": 58},
        "healthcare": {"demand": 74, "competition": 70, "cpcPressure": 66, "macro": 62},
        "education": {"demand": 68, "competition": 62, "cpcPressure": 57, "macro": 64},
        "ecommerce": {"demand": 71, "competition": 85, "cpcPressure": 82, "macro": 56},
        "consulting": {"demand": 64, "competition": 69, "cpcPressure": 60, "macro": 61},
        "marketing": {"demand": 67, "competition": 77, "cpcPressure": 72, "macro": 60},
        "real estate": {"demand": 58, "competition": 63, "cpcPressure": 68, "macro": 52},
        "logistics": {"demand": 66, "competition": 59, "cpcPressure": 54, "macro": 57},
        "default": {"demand": 63, "competition": 64, "cpcPressure": 60, "macro": 58},
    }

    _DELIVERY_ADJUSTMENTS = {
        "saas": {"demand": 6, "competition": 8, "cpcPressure": 7, "macro": 0},
        "service": {"demand": 2, "competition": 2, "cpcPressure": 1, "macro": 2},
        "marketplace": {"demand": 4, "competition": 7, "cpcPressure": 6, "macro": -1},
        "physical": {"demand": 1, "competition": 3, "cpcPressure": 2, "macro": -2},
        "digital": {"demand": 3, "competition": 4, "cpcPressure": 3, "macro": 1},
        "default": {"demand": 0, "competition": 0, "cpcPressure": 0, "macro": 0},
    }

    _MARKET_SEGMENT_ADJUSTMENTS = {
        "b2b": {"demand": -2, "competition": -1, "cpcPressure": 2, "macro": 3},
        "b2c": {"demand": 3, "competition": 4, "cpcPressure": 5, "macro": -1},
        "b2g": {"demand": -3, "competition": -2, "cpcPressure": 1, "macro": 2},
        "default": {"demand": 0, "competition": 0, "cpcPressure": 0, "macro": 0},
    }

    _LOCATION_ADJUSTMENTS = {
        "global": {"demand": 7, "competition": 10, "cpcPressure": 8, "macro": 2},
        "usa": {"demand": 5, "competition": 7, "cpcPressure": 6, "macro": 1},
        "us": {"demand": 5, "competition": 7, "cpcPressure": 6, "macro": 1},
        "nigeria": {"demand": 2, "competition": -1, "cpcPressure": -2, "macro": -2},
        "uk": {"demand": 3, "competition": 4, "cpcPressure": 4, "macro": 1},
        "canada": {"demand": 2, "competition": 2, "cpcPressure": 1, "macro": 1},
        "default": {"demand": 0, "competition": 0, "cpcPressure": 0, "macro": 0},
    }

    @staticmethod
    def _norm_key(value: str) -> str:
        return (value or "").strip().lower()

    @staticmethod
    def _clamp_score(value: float) -> int:
        return max(0, min(100, int(round(value))))

    @staticmethod
    def _apply_adjustments(base: Dict[str, int], *adjustments: Dict[str, int]) -> Dict[str, int]:
        out = dict(base)
        for adj in adjustments:
            for k in out.keys():
                out[k] += int(adj.get(k, 0))
        for k, v in out.items():
            out[k] = MarketDataService._clamp_score(v)
        return out

    @staticmethod
    def _read_override_from_file(context_key: str) -> Dict[str, Any] | None:
        """Optional local override file for fresher market facts.

        File format (JSON):
        {
          "overrides": {
            "<context_key>": {
              "demand": 72,
              "competition": 66,
              "cpcPressure": 58,
              "macro": 61,
              "updatedAt": "2026-03-08T00:00:00Z",
              "source": "manual"
            }
          }
        }
        """
        path = os.environ.get("MARKET_DATA_OVERRIDES_FILE", "").strip()
        if not path:
            return None
        if not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            overrides = payload.get("overrides", {})
            return overrides.get(context_key)
        except Exception:
            return None

    @staticmethod
    def get_market_profile(
        *,
        industry: str,
        sub_industry: str | None,
        service_type: str | None,
        delivery_model: str,
        target_market: str,
        target_location: str,
    ) -> Dict[str, Any]:
        """Return normalized market context for deterministic scoring."""
        industry_key = MarketDataService._norm_key(sub_industry or industry)
        delivery_key = MarketDataService._norm_key(delivery_model)
        market_key = MarketDataService._norm_key(target_market)
        location_key = MarketDataService._norm_key(target_location)
        service_key = MarketDataService._norm_key(service_type or "")

        base = MarketDataService._INDUSTRY_BASELINES.get(
            industry_key, MarketDataService._INDUSTRY_BASELINES.get(MarketDataService._norm_key(industry), MarketDataService._INDUSTRY_BASELINES["default"])
        )
        delivery_adj = MarketDataService._DELIVERY_ADJUSTMENTS.get(delivery_key, MarketDataService._DELIVERY_ADJUSTMENTS["default"])
        market_adj = MarketDataService._MARKET_SEGMENT_ADJUSTMENTS.get(market_key, MarketDataService._MARKET_SEGMENT_ADJUSTMENTS["default"])
        location_adj = MarketDataService._LOCATION_ADJUSTMENTS.get(location_key, MarketDataService._LOCATION_ADJUSTMENTS["default"])

        factors = MarketDataService._apply_adjustments(base, delivery_adj, market_adj, location_adj)

        # Service-type signal (service-specific context bias)
        if service_key:
            if any(t in service_key for t in ["automation", "ai", "analytics", "software"]):
                factors["demand"] = MarketDataService._clamp_score(factors["demand"] + 3)
                factors["competition"] = MarketDataService._clamp_score(factors["competition"] + 4)
            elif any(t in service_key for t in ["consult", "agency", "virtual assistant", "bookkeeping"]):
                factors["competition"] = MarketDataService._clamp_score(factors["competition"] + 2)
                factors["cpcPressure"] = MarketDataService._clamp_score(factors["cpcPressure"] - 1)

        context_key = "|".join(
            [industry_key or "na", service_key or "na", delivery_key or "na", market_key or "na", location_key or "na"]
        )
        override = MarketDataService._read_override_from_file(context_key)
        source = "baseline_rules"
        updated_at = datetime.now(timezone.utc).isoformat()
        if override:
            source = override.get("source", "override_file")
            updated_at = override.get("updatedAt", updated_at)
            factors = {
                "demand": MarketDataService._clamp_score(override.get("demand", factors["demand"])),
                "competition": MarketDataService._clamp_score(override.get("competition", factors["competition"])),
                "cpcPressure": MarketDataService._clamp_score(override.get("cpcPressure", factors["cpcPressure"])),
                "macro": MarketDataService._clamp_score(override.get("macro", factors["macro"])),
            }

        # Competition and CPC are risk factors; invert for "goodness" use in scoring.
        opportunity_from_market = MarketDataService._clamp_score(
            factors["demand"] * 0.40 +
            (100 - factors["competition"]) * 0.25 +
            (100 - factors["cpcPressure"]) * 0.20 +
            factors["macro"] * 0.15
        )

        return {
            "contextKey": context_key,
            "factors": factors,
            "marketScore": opportunity_from_market,
            "source": source,
            "updatedAt": updated_at,
            "weights": {
                "demand": 0.40,
                "competition_inverse": 0.25,
                "cpc_inverse": 0.20,
                "macro": 0.15,
            },
        }

