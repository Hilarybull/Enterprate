"""Website Analytics Service for tracking visits, leads, and conversions"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from app.core.database import get_db


class WebsiteAnalyticsService:
    """
    Service for tracking and analyzing website performance.
    Tracks page views, visitors, leads captured, and conversion rates.
    """
    
    @staticmethod
    async def record_page_view(
        website_id: str,
        workspace_id: str,
        visitor_id: str,
        page_path: str = "/",
        referrer: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_country: Optional[str] = None,
        device_type: str = "desktop"
    ) -> dict:
        """Record a page view event"""
        db = get_db()
        
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        event = {
            "id": event_id,
            "websiteId": website_id,
            "workspace_id": workspace_id,
            "visitorId": visitor_id,
            "eventType": "page_view",
            "pagePath": page_path,
            "referrer": referrer,
            "userAgent": user_agent,
            "country": ip_country,
            "deviceType": device_type,
            "timestamp": now
        }
        
        await db.website_analytics.insert_one(event)
        
        # Update website stats
        await db.ai_websites.update_one(
            {"id": website_id},
            {
                "$inc": {"stats.pageViews": 1},
                "$set": {"stats.lastVisit": now}
            }
        )
        
        return {k: v for k, v in event.items() if k != '_id'}
    
    @staticmethod
    async def record_lead_conversion(
        website_id: str,
        workspace_id: str,
        visitor_id: str,
        lead_id: str,
        conversion_type: str = "form_submit"
    ) -> dict:
        """Record a lead conversion event"""
        db = get_db()
        
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        event = {
            "id": event_id,
            "websiteId": website_id,
            "workspace_id": workspace_id,
            "visitorId": visitor_id,
            "eventType": "conversion",
            "conversionType": conversion_type,
            "leadId": lead_id,
            "timestamp": now
        }
        
        await db.website_analytics.insert_one(event)
        
        # Update website stats
        await db.ai_websites.update_one(
            {"id": website_id},
            {
                "$inc": {"stats.conversions": 1, "stats.leadsGenerated": 1},
                "$set": {"stats.lastConversion": now}
            }
        )
        
        return {k: v for k, v in event.items() if k != '_id'}
    
    @staticmethod
    async def get_website_analytics(
        website_id: str,
        workspace_id: str,
        days: int = 30
    ) -> dict:
        """Get comprehensive analytics for a website"""
        db = get_db()
        
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get events in date range
        events = await db.website_analytics.find({
            "websiteId": website_id,
            "workspace_id": workspace_id,
            "timestamp": {"$gte": start_date.isoformat()}
        }).to_list(length=10000)
        
        # Calculate metrics
        page_views = len([e for e in events if e.get("eventType") == "page_view"])
        conversions = len([e for e in events if e.get("eventType") == "conversion"])
        unique_visitors = len(set(e.get("visitorId") for e in events))
        
        # Calculate conversion rate
        conversion_rate = (conversions / unique_visitors * 100) if unique_visitors > 0 else 0
        
        # Get daily breakdown
        daily_stats = {}
        for event in events:
            date = event.get("timestamp", "")[:10]
            if date not in daily_stats:
                daily_stats[date] = {"pageViews": 0, "conversions": 0, "visitors": set()}
            
            daily_stats[date]["visitors"].add(event.get("visitorId"))
            if event.get("eventType") == "page_view":
                daily_stats[date]["pageViews"] += 1
            elif event.get("eventType") == "conversion":
                daily_stats[date]["conversions"] += 1
        
        # Convert daily stats to list
        daily_data = []
        for date in sorted(daily_stats.keys()):
            stats = daily_stats[date]
            daily_data.append({
                "date": date,
                "pageViews": stats["pageViews"],
                "conversions": stats["conversions"],
                "visitors": len(stats["visitors"])
            })
        
        # Get referrer breakdown
        referrers = {}
        for event in events:
            if event.get("eventType") == "page_view" and event.get("referrer"):
                ref = event.get("referrer", "Direct")
                referrers[ref] = referrers.get(ref, 0) + 1
        
        top_referrers = sorted(referrers.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get device breakdown
        devices = {}
        for event in events:
            if event.get("eventType") == "page_view":
                device = event.get("deviceType", "unknown")
                devices[device] = devices.get(device, 0) + 1
        
        # Get country breakdown
        countries = {}
        for event in events:
            if event.get("eventType") == "page_view" and event.get("country"):
                country = event.get("country", "Unknown")
                countries[country] = countries.get(country, 0) + 1
        
        top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get leads
        leads = await db.leads.find({
            "workspace_id": workspace_id,
            "source": "website_form",
            "createdAt": {"$gte": start_date.isoformat()}
        }).to_list(length=100)
        
        return {
            "websiteId": website_id,
            "period": f"{days} days",
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "summary": {
                "pageViews": page_views,
                "uniqueVisitors": unique_visitors,
                "conversions": conversions,
                "conversionRate": round(conversion_rate, 2),
                "leadsGenerated": len(leads)
            },
            "dailyData": daily_data,
            "referrers": [{"source": r[0], "count": r[1]} for r in top_referrers],
            "devices": devices,
            "countries": [{"country": c[0], "count": c[1]} for c in top_countries],
            "recentLeads": [
                {
                    "id": l.get("id"),
                    "name": l.get("name"),
                    "email": l.get("email"),
                    "createdAt": l.get("createdAt")
                }
                for l in sorted(leads, key=lambda x: x.get("createdAt", ""), reverse=True)[:10]
            ]
        }
    
    @staticmethod
    async def get_all_websites_analytics(
        workspace_id: str,
        days: int = 30
    ) -> dict:
        """Get analytics overview for all websites in a workspace"""
        db = get_db()
        
        # Get all websites
        websites = await db.ai_websites.find({
            "workspace_id": workspace_id
        }).to_list(length=100)
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get all events for workspace
        events = await db.website_analytics.find({
            "workspace_id": workspace_id,
            "timestamp": {"$gte": start_date.isoformat()}
        }).to_list(length=50000)
        
        # Get all leads
        leads = await db.leads.find({
            "workspace_id": workspace_id,
            "source": "website_form",
            "createdAt": {"$gte": start_date.isoformat()}
        }).to_list(length=500)
        
        # Calculate totals
        total_page_views = len([e for e in events if e.get("eventType") == "page_view"])
        total_conversions = len([e for e in events if e.get("eventType") == "conversion"])
        total_visitors = len(set(e.get("visitorId") for e in events))
        
        # Per-website breakdown
        website_stats = []
        for website in websites:
            website_events = [e for e in events if e.get("websiteId") == website.get("id")]
            website_leads = [l for l in leads if l.get("websiteId") == website.get("id")]
            
            views = len([e for e in website_events if e.get("eventType") == "page_view"])
            convs = len([e for e in website_events if e.get("eventType") == "conversion"])
            visitors = len(set(e.get("visitorId") for e in website_events))
            
            website_stats.append({
                "websiteId": website.get("id"),
                "name": website.get("businessContext", {}).get("companyName", "Untitled"),
                "deploymentUrl": website.get("deploymentUrl"),
                "status": website.get("status"),
                "pageViews": views,
                "visitors": visitors,
                "conversions": convs,
                "leads": len(website_leads),
                "conversionRate": round((convs / visitors * 100) if visitors > 0 else 0, 2)
            })
        
        # Sort by page views
        website_stats.sort(key=lambda x: x["pageViews"], reverse=True)
        
        return {
            "period": f"{days} days",
            "summary": {
                "totalWebsites": len(websites),
                "deployedWebsites": len([w for w in websites if w.get("status") == "deployed"]),
                "totalPageViews": total_page_views,
                "totalVisitors": total_visitors,
                "totalConversions": total_conversions,
                "totalLeads": len(leads),
                "averageConversionRate": round((total_conversions / total_visitors * 100) if total_visitors > 0 else 0, 2)
            },
            "websites": website_stats
        }
    
    @staticmethod
    async def get_realtime_visitors(website_id: str, workspace_id: str) -> dict:
        """Get real-time visitor information (last 5 minutes)"""
        db = get_db()
        
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        
        events = await db.website_analytics.find({
            "websiteId": website_id,
            "workspace_id": workspace_id,
            "eventType": "page_view",
            "timestamp": {"$gte": cutoff}
        }).to_list(length=1000)
        
        active_visitors = len(set(e.get("visitorId") for e in events))
        
        return {
            "websiteId": website_id,
            "activeVisitors": active_visitors,
            "recentPageViews": len(events),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
