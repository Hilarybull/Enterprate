"""Community intelligence service (real data only, no fabricated values)."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.schemas.validation_report import ValidationReportCreate


class CommunityIntelService:
    """Fetch community signals from live endpoints where possible."""

    @staticmethod
    def _seed_terms(data: ValidationReportCreate) -> List[str]:
        terms: List[str] = []
        if data.subIndustry:
            terms.append(data.subIndustry.strip().lower())
        if data.serviceType:
            terms.append(data.serviceType.strip().lower())
        if data.industry:
            terms.append(data.industry.strip().lower())
        if data.deliveryModel:
            terms.append(data.deliveryModel.strip().lower())
        dedup = []
        seen = set()
        for t in terms:
            if t and t not in seen:
                seen.add(t)
                dedup.append(t)
        return dedup[:4]

    @staticmethod
    def _community_score(total_members: int) -> int:
        # Real-data-derived score only.
        if total_members >= 5_000_000:
            return 9
        if total_members >= 1_000_000:
            return 8
        if total_members >= 250_000:
            return 7
        if total_members >= 50_000:
            return 6
        if total_members >= 10_000:
            return 5
        if total_members > 0:
            return 4
        return 0

    @staticmethod
    async def _reddit_signal(terms: List[str]) -> Optional[Tuple[str, int]]:
        if not terms:
            return None
        q = " ".join(terms[:2])
        url = "https://www.reddit.com/subreddits/search.json"
        params = {"q": q, "limit": 6, "sort": "relevance"}
        headers = {"User-Agent": "EnterprateAI/1.0 (community-intel)"}
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return None

        children = (((data or {}).get("data") or {}).get("children") or [])
        members = 0
        count = 0
        for item in children:
            sd = (item or {}).get("data") or {}
            subs = sd.get("subscribers")
            if isinstance(subs, int):
                members += subs
                count += 1

        if count == 0:
            return None
        details = f"{count} relevant subreddits - {members:,} members"
        return details, members

    @staticmethod
    async def _youtube_signal(terms: List[str]) -> Optional[Tuple[str, int]]:
        api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
        if not api_key or not terms:
            return None
        q = " ".join(terms[:2])
        search_url = "https://www.googleapis.com/youtube/v3/search"
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                s = await client.get(
                    search_url,
                    params={
                        "part": "snippet",
                        "q": q,
                        "type": "channel",
                        "maxResults": 5,
                        "key": api_key,
                    },
                )
                s.raise_for_status()
                sdata = s.json()
                items = sdata.get("items", []) or []
                channel_ids = [
                    (it.get("id") or {}).get("channelId")
                    for it in items
                    if (it.get("id") or {}).get("channelId")
                ]
                if not channel_ids:
                    return None

                c = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={
                        "part": "statistics",
                        "id": ",".join(channel_ids),
                        "maxResults": 5,
                        "key": api_key,
                    },
                )
                c.raise_for_status()
                cdata = c.json()
        except Exception:
            return None

        total_subs = 0
        count = 0
        for it in cdata.get("items", []) or []:
            stats = it.get("statistics") or {}
            subs = stats.get("subscriberCount")
            try:
                if subs is not None:
                    total_subs += int(subs)
                    count += 1
            except Exception:
                continue
        if count == 0:
            return None
        return f"{count} relevant channels - {total_subs:,} subscribers", total_subs

    @staticmethod
    async def _facebook_signal(terms: List[str]) -> Optional[Tuple[str, int]]:
        token = os.environ.get("FACEBOOK_GRAPH_TOKEN", "").strip()
        if not token or not terms:
            return None
        q = " ".join(terms[:2])
        url = "https://graph.facebook.com/v20.0/search"
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                r = await client.get(
                    url,
                    params={
                        "type": "page",
                        "q": q,
                        "fields": "name,fan_count",
                        "limit": 5,
                        "access_token": token,
                    },
                )
                r.raise_for_status()
                data = r.json()
        except Exception:
            return None

        rows = data.get("data", []) or []
        fans = 0
        count = 0
        for row in rows:
            fc = row.get("fan_count")
            try:
                if fc is not None:
                    fans += int(fc)
                    count += 1
            except Exception:
                continue
        if count == 0:
            return None
        return f"{count} relevant pages - {fans:,} followers", fans

    @staticmethod
    async def _linkedin_signal(terms: List[str]) -> Optional[Tuple[str, int]]:
        """LinkedIn live proxy via Bing Web Search API (site-filtered)."""
        key = os.environ.get("BING_SEARCH_API_KEY", "").strip()
        if not key or not terms:
            return None
        q = f"site:linkedin.com/groups {' '.join(terms[:2])}"
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": key}
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                r = await client.get(url, params={"q": q, "count": 10, "responseFilter": "Webpages"})
                r.raise_for_status()
                data = r.json()
        except Exception:
            return None

        web = data.get("webPages") or {}
        estimated = web.get("totalEstimatedMatches")
        rows = web.get("value") or []
        if estimated is None and not rows:
            return None
        est = int(estimated or len(rows))
        # proxy scale, not member count
        return f"{est:,} indexed LinkedIn group/page results (live search index)", est

    @staticmethod
    async def get_community_signals(data: ValidationReportCreate) -> Dict[str, Any]:
        """Return live community signals, with explicit unavailable statuses."""
        terms = CommunityIntelService._seed_terms(data)

        rows: List[Dict[str, Any]] = []
        source_status = {}

        reddit = await CommunityIntelService._reddit_signal(terms)
        if reddit:
            details, members = reddit
            rows.append({"platform": "Reddit", "details": details, "score": CommunityIntelService._community_score(members)})
            source_status["reddit"] = "live"
        else:
            rows.append({"platform": "Reddit", "details": "Unavailable (live fetch failed)", "score": 0})
            source_status["reddit"] = "unavailable"

        youtube = await CommunityIntelService._youtube_signal(terms)
        if youtube:
            details, subs = youtube
            rows.append({"platform": "YouTube", "details": details, "score": CommunityIntelService._community_score(subs)})
            source_status["youtube"] = "live"
        else:
            rows.append({"platform": "YouTube", "details": "Unavailable (set YOUTUBE_API_KEY)", "score": 0})
            source_status["youtube"] = "unavailable"

        facebook = await CommunityIntelService._facebook_signal(terms)
        if facebook:
            details, fans = facebook
            rows.append({"platform": "Facebook", "details": details, "score": CommunityIntelService._community_score(fans)})
            source_status["facebook"] = "live"
        else:
            rows.append({"platform": "Facebook", "details": "Unavailable (set FACEBOOK_GRAPH_TOKEN)", "score": 0})
            source_status["facebook"] = "unavailable"

        linkedin = await CommunityIntelService._linkedin_signal(terms)
        if linkedin:
            details, est = linkedin
            rows.append({"platform": "LinkedIn", "details": details, "score": CommunityIntelService._community_score(est)})
            source_status["linkedin"] = "live_proxy"
        else:
            rows.append({"platform": "LinkedIn", "details": "Unavailable (set BING_SEARCH_API_KEY for live index signal)", "score": 0})
            source_status["linkedin"] = "unavailable"

        return {
            "signals": rows,
            "sourceStatus": source_status,
        }
