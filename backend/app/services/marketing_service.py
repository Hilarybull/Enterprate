"""Marketing/Growth service - Campaigns, Social, Analytics"""
import uuid
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.marketing import (
    CampaignCreate, CampaignUpdate, CampaignStatus,
    SocialPostCreate, SocialPostUpdate, SocialPostGenerateRequest,
    AnalyticsRequest, AnalyticsPeriod
)

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class MarketingService:
    """Service for Marketing/Growth operations"""
    
    # === CAMPAIGN MANAGEMENT ===
    
    @staticmethod
    async def create_campaign(workspace_id: str, user_id: str, data: CampaignCreate) -> dict:
        """Create a marketing campaign"""
        db = get_db()
        
        campaign_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        campaign = {
            "id": campaign_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "description": data.description,
            "type": data.type.value if hasattr(data.type, 'value') else data.type,
            "status": "draft",
            "budget": data.budget,
            "startDate": data.startDate,
            "endDate": data.endDate,
            "targetAudience": data.targetAudience,
            "goals": data.goals,
            "channels": data.channels,
            "metrics": {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "spend": 0.0,
                "ctr": 0.0,
                "cpc": 0.0,
                "roi": 0.0
            },
            "created_by": user_id,
            "createdAt": now
        }
        
        await db.campaigns.insert_one(campaign)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "campaign.created",
            "data": {"campaign_id": campaign_id, "name": data.name},
            "occurredAt": now
        })
        
        return {k: v for k, v in campaign.items() if k != '_id'}
    
    @staticmethod
    async def get_campaigns(workspace_id: str, status: Optional[str] = None) -> List[dict]:
        """Get campaigns for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if status:
            query["status"] = status
        
        campaigns = await db.campaigns.find(query).sort("createdAt", -1).to_list(length=100)
        return [{k: v for k, v in c.items() if k != '_id'} for c in campaigns]
    
    @staticmethod
    async def get_campaign(campaign_id: str, workspace_id: str) -> dict:
        """Get a specific campaign"""
        db = get_db()
        
        campaign = await db.campaigns.find_one({
            "id": campaign_id,
            "workspace_id": workspace_id
        })
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {k: v for k, v in campaign.items() if k != '_id'}
    
    @staticmethod
    async def update_campaign(campaign_id: str, workspace_id: str, data: CampaignUpdate) -> dict:
        """Update a campaign"""
        db = get_db()
        
        campaign = await db.campaigns.find_one({
            "id": campaign_id,
            "workspace_id": workspace_id
        })
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data and hasattr(update_data["status"], 'value'):
            update_data["status"] = update_data["status"].value
        
        if update_data:
            await db.campaigns.update_one(
                {"id": campaign_id},
                {"$set": update_data}
            )
        
        updated = await db.campaigns.find_one({"id": campaign_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_campaign(campaign_id: str, workspace_id: str) -> bool:
        """Delete a campaign"""
        db = get_db()
        result = await db.campaigns.delete_one({
            "id": campaign_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def update_campaign_metrics(campaign_id: str, workspace_id: str, metrics: dict) -> dict:
        """Update campaign metrics"""
        db = get_db()
        
        campaign = await db.campaigns.find_one({
            "id": campaign_id,
            "workspace_id": workspace_id
        })
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Calculate derived metrics
        impressions = metrics.get("impressions", campaign["metrics"].get("impressions", 0))
        clicks = metrics.get("clicks", campaign["metrics"].get("clicks", 0))
        spend = metrics.get("spend", campaign["metrics"].get("spend", 0))
        conversions = metrics.get("conversions", campaign["metrics"].get("conversions", 0))
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0
        
        updated_metrics = {
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "spend": spend,
            "ctr": round(ctr, 2),
            "cpc": round(cpc, 2),
            "roi": metrics.get("roi", 0)
        }
        
        await db.campaigns.update_one(
            {"id": campaign_id},
            {"$set": {"metrics": updated_metrics}}
        )
        
        updated = await db.campaigns.find_one({"id": campaign_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    # === SOCIAL MEDIA POSTS ===
    
    @staticmethod
    async def create_social_post(workspace_id: str, user_id: str, data: SocialPostCreate) -> dict:
        """Create a social media post"""
        db = get_db()
        
        post_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        post = {
            "id": post_id,
            "workspace_id": workspace_id,
            "platform": data.platform,
            "content": data.content,
            "status": "draft",
            "scheduledFor": data.scheduledFor,
            "postedAt": None,
            "campaignId": data.campaignId,
            "mediaUrls": data.mediaUrls,
            "hashtags": data.hashtags,
            "created_by": user_id,
            "createdAt": now
        }
        
        await db.social_posts.insert_one(post)
        return {k: v for k, v in post.items() if k != '_id'}
    
    @staticmethod
    async def get_social_posts(workspace_id: str, platform: Optional[str] = None, campaign_id: Optional[str] = None) -> List[dict]:
        """Get social posts"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if platform:
            query["platform"] = platform
        if campaign_id:
            query["campaignId"] = campaign_id
        
        posts = await db.social_posts.find(query).sort("createdAt", -1).to_list(length=200)
        return [{k: v for k, v in p.items() if k != '_id'} for p in posts]
    
    @staticmethod
    async def update_social_post(post_id: str, workspace_id: str, data: SocialPostUpdate) -> dict:
        """Update a social post"""
        db = get_db()
        
        post = await db.social_posts.find_one({
            "id": post_id,
            "workspace_id": workspace_id
        })
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await db.social_posts.update_one(
                {"id": post_id},
                {"$set": update_data}
            )
        
        updated = await db.social_posts.find_one({"id": post_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_social_post(post_id: str, workspace_id: str) -> bool:
        """Delete a social post"""
        db = get_db()
        result = await db.social_posts.delete_one({
            "id": post_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def generate_social_post(workspace_id: str, data: SocialPostGenerateRequest) -> dict:
        """Generate social post content with AI"""
        if not LLM_AVAILABLE:
            return MarketingService._get_fallback_social_post(data)
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return MarketingService._get_fallback_social_post(data)
            
            platform_limits = {
                "twitter": 280,
                "linkedin": 3000,
                "facebook": 63206,
                "instagram": 2200
            }
            
            char_limit = platform_limits.get(data.platform.lower(), 500)
            
            prompt = f"""Generate a social media post for {data.platform}.
            
            Topic: {data.topic}
            Tone: {data.tone}
            Character limit: {char_limit}
            Include emojis: {data.includeEmojis}
            Include hashtags: {data.includeHashtags}
            
            Return a JSON object with:
            - content: the post text
            - hashtags: array of relevant hashtags (without #)
            
            Return ONLY valid JSON."""
            
            chat = LlmChat(
                api_key=llm_key,
                model="gpt-4o",
                system_message="You are a social media marketing expert. Create engaging, platform-appropriate content."
            )
            
            response = await chat.send_async(message=UserMessage(text=prompt))
            
            import json
            try:
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                
                result = json.loads(text.strip())
                return {
                    "platform": data.platform,
                    "content": result.get("content", ""),
                    "hashtags": result.get("hashtags", []),
                    "generated": True
                }
            except Exception:
                return MarketingService._get_fallback_social_post(data)
                
        except Exception as e:
            print(f"Social post generation error: {e}")
            return MarketingService._get_fallback_social_post(data)
    
    @staticmethod
    def _get_fallback_social_post(data: SocialPostGenerateRequest) -> dict:
        """Fallback social post content"""
        emojis = "🚀 " if data.includeEmojis else ""
        return {
            "platform": data.platform,
            "content": f"{emojis}Check out our latest update on {data.topic}! We're excited to share this with you.",
            "hashtags": ["business", "growth", data.topic.replace(" ", "").lower()[:20]],
            "generated": False
        }
    
    # === ANALYTICS ===
    
    @staticmethod
    async def get_growth_analytics(workspace_id: str, period: str = "month") -> dict:
        """Get comprehensive growth analytics"""
        db = get_db()
        
        # Get leads data
        leads = await db.leads.find({"workspace_id": workspace_id}).to_list(length=1000)
        
        lead_by_source = {}
        lead_by_status = {"NEW": 0, "CONTACTED": 0, "QUALIFIED": 0, "CONVERTED": 0, "LOST": 0}
        
        for lead in leads:
            source = lead.get("source", "OTHER")
            lead_by_source[source] = lead_by_source.get(source, 0) + 1
            status = lead.get("status", "NEW")
            lead_by_status[status] = lead_by_status.get(status, 0) + 1
        
        converted = lead_by_status.get("CONVERTED", 0)
        conversion_rate = (converted / len(leads) * 100) if leads else 0
        
        # Get campaign data
        campaigns = await db.campaigns.find({"workspace_id": workspace_id}).to_list(length=100)
        
        active_campaigns = [c for c in campaigns if c.get("status") == "active"]
        total_budget = sum(c.get("budget", 0) or 0 for c in campaigns)
        total_spend = sum(c.get("metrics", {}).get("spend", 0) for c in campaigns)
        
        # Calculate average ROI
        rois = [c.get("metrics", {}).get("roi", 0) for c in campaigns if c.get("metrics", {}).get("roi", 0) > 0]
        avg_roi = sum(rois) / len(rois) if rois else 0
        
        # Top performing campaigns
        sorted_campaigns = sorted(
            campaigns,
            key=lambda c: c.get("metrics", {}).get("conversions", 0),
            reverse=True
        )[:5]
        
        top_performing = [
            {"id": c["id"], "name": c["name"], "conversions": c.get("metrics", {}).get("conversions", 0)}
            for c in sorted_campaigns
        ]
        
        return {
            "period": period,
            "leads": {
                "totalLeads": len(leads),
                "newLeads": lead_by_status.get("NEW", 0),
                "convertedLeads": converted,
                "conversionRate": round(conversion_rate, 2),
                "leadsBySource": lead_by_source,
                "leadsByStatus": lead_by_status,
                "trend": []  # Would require time-series data
            },
            "campaigns": {
                "totalCampaigns": len(campaigns),
                "activeCampaigns": len(active_campaigns),
                "totalBudget": total_budget,
                "totalSpend": total_spend,
                "avgROI": round(avg_roi, 2),
                "topPerforming": top_performing
            },
            "summary": {
                "leadsThisMonth": len(leads),  # Simplified - would filter by date
                "campaignsActive": len(active_campaigns),
                "budgetRemaining": total_budget - total_spend,
                "overallConversionRate": round(conversion_rate, 2)
            }
        }
    
    @staticmethod
    async def get_lead_trends(workspace_id: str, days: int = 30) -> List[dict]:
        """Get lead trends over time"""
        db = get_db()
        
        # Get leads from the last N days
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        leads = await db.leads.find({
            "workspace_id": workspace_id,
            "created_at": {"$gte": start_date.isoformat()}
        }).to_list(length=1000)
        
        # Group by date
        daily_counts = {}
        for i in range(days):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_counts[date] = 0
        
        for lead in leads:
            created = lead.get("created_at", "")
            if created:
                date = created[:10]  # Get YYYY-MM-DD
                if date in daily_counts:
                    daily_counts[date] += 1
        
        return [
            {"date": date, "count": count}
            for date, count in sorted(daily_counts.items())
        ]
