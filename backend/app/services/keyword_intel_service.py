"""Keyword intelligence service backed by DataForSEO."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

from app.schemas.validation_report import ValidationReportCreate


class KeywordIntelService:
    """Fetch top keyword metrics from DataForSEO and normalize for report UI."""

    _ENDPOINT = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live"

    _LOCATION_MAP = {
        "uk": "United Kingdom",
        "united kingdom": "United Kingdom",
        "us": "United States",
        "usa": "United States",
        "united states": "United States",
        "nigeria": "Nigeria",
        "canada": "Canada",
    }

    @staticmethod
    def _norm_location(raw: str) -> str:
        key = (raw or "").strip().lower()
        return KeywordIntelService._LOCATION_MAP.get(key, raw or "United Kingdom")

    @staticmethod
    def _format_volume(volume: Optional[float]) -> str:
        if volume is None:
            return "N/A"
        v = float(volume)
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f}M"
        if v >= 1_000:
            return f"{v/1_000:.1f}K"
        return str(int(round(v)))

    @staticmethod
    def _competition_label(value: Optional[float]) -> str:
        if value is None:
            return "MEDIUM"
        c = float(value)
        # DataForSEO competition often 0..1, but handle 0..100 defensively.
        if c > 1:
            if c >= 66:
                return "HIGH"
            if c >= 33:
                return "MEDIUM"
            return "LOW"
        if c >= 0.67:
            return "HIGH"
        if c >= 0.34:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _extract_growth(item: Dict[str, Any]) -> Optional[str]:
        trend = item.get("search_volume_trend") or {}
        monthly = trend.get("monthly")
        if isinstance(monthly, (int, float)):
            sign = "+" if monthly >= 0 else ""
            return f"{sign}{round(float(monthly), 1)}%"

        monthly_searches = item.get("monthly_searches") or []
        if isinstance(monthly_searches, list) and len(monthly_searches) >= 2:
            try:
                a = float(monthly_searches[0].get("search_volume") or 0)
                b = float(monthly_searches[1].get("search_volume") or 0)
                if b > 0:
                    pct = ((a - b) / b) * 100
                    sign = "+" if pct >= 0 else ""
                    return f"{sign}{round(pct, 1)}%"
            except Exception:
                return None
        return None

    @staticmethod
    def _seed_keywords(data: ValidationReportCreate) -> List[str]:
        seeds: List[str] = []
        if data.serviceType:
            seeds.append(data.serviceType.strip().lower())
        if data.subIndustry:
            seeds.append(data.subIndustry.strip().lower())
        if data.industry and data.deliveryModel:
            seeds.append(f"{data.industry.strip().lower()} {data.deliveryModel.strip().lower()}")
        if data.ideaDescription:
            words = " ".join(data.ideaDescription.strip().lower().split()[:5])
            if words:
                seeds.append(words)
        if data.problemSolved:
            words = " ".join(data.problemSolved.strip().lower().split()[:5])
            if words:
                seeds.append(words)

        # Deduplicate while preserving order
        deduped: List[str] = []
        seen = set()
        for s in seeds:
            if s and s not in seen:
                seen.add(s)
                deduped.append(s)
        return deduped[:8]

    @staticmethod
    async def get_top_keywords(data: ValidationReportCreate) -> Optional[Dict[str, Any]]:
        login = os.environ.get("DATAFORSEO_LOGIN", "").strip()
        password = os.environ.get("DATAFORSEO_PASSWORD", "").strip()
        if not login or not password:
            return None

        keywords = KeywordIntelService._seed_keywords(data)
        if not keywords:
            return None

        payload = [{
            "location_name": KeywordIntelService._norm_location(data.targetLocation),
            "language_name": "English",
            "keywords": keywords,
        }]

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    KeywordIntelService._ENDPOINT,
                    json=payload,
                    auth=httpx.BasicAuth(login, password),
                )
                response.raise_for_status()
                body = response.json()
        except Exception:
            return None

        items: List[Dict[str, Any]] = []
        for task in body.get("tasks", []) or []:
            for result in task.get("result", []) or []:
                items.extend(result.get("items", []) or [])
        if not items:
            return None

        rows: List[Dict[str, Any]] = []
        for item in items:
            keyword = item.get("keyword")
            info = item.get("keyword_info") or {}
            volume = info.get("search_volume")
            competition = info.get("competition")
            growth = KeywordIntelService._extract_growth(item)
            if keyword:
                rows.append({
                    "keyword": str(keyword),
                    "volume_num": float(volume) if volume is not None else 0.0,
                    "volume": KeywordIntelService._format_volume(volume),
                    "competition": KeywordIntelService._competition_label(competition),
                    "growth": growth,
                })

        if not rows:
            return None

        rows.sort(key=lambda r: r["volume_num"], reverse=True)
        top = rows[:3]
        top_keywords = [
            {
                "keyword": r["keyword"],
                "volume": r["volume"],
                "competition": r["competition"],
                **({"growth": r["growth"]} if r.get("growth") else {}),
            }
            for r in top
        ]

        trend = top[0]
        return {
            "source": "dataforseo",
            "topKeywords": top_keywords,
            "trendKeyword": trend["keyword"],
            "trendVolume": trend["volume"],
            "trendGrowth": trend.get("growth"),
        }

