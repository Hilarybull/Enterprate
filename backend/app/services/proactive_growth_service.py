"""Proactive Growth Agent Service - AI-powered business monitoring and growth recommendations"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.core.database import get_db

# Try to import LLM
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class ProactiveGrowthService:
    """
    AI-powered Growth Agent that monitors business performance and 
    proactively suggests/triggers growth activities with user approval.
    """
    
    # Performance thresholds
    LEAD_DECLINE_THRESHOLD = 0.2  # 20% decline triggers alert
    CONVERSION_DECLINE_THRESHOLD = 0.15  # 15% decline triggers alert
    REVENUE_DECLINE_THRESHOLD = 0.1  # 10% decline triggers alert
    
    @staticmethod
    async def analyze_business_performance(workspace_id: str) -> dict:
        """
        Analyze business performance metrics and detect downturns.
        Returns performance data with trend analysis.
        """
        db = get_db()
        now = datetime.now(timezone.utc)
        
        # Get data for last 30 days vs previous 30 days
        current_period_start = now - timedelta(days=30)
        previous_period_start = now - timedelta(days=60)
        previous_period_end = now - timedelta(days=30)
        
        # Analyze leads
        leads_analysis = await ProactiveGrowthService._analyze_leads(
            db, workspace_id, current_period_start, previous_period_start, previous_period_end
        )
        
        # Analyze invoices/revenue
        revenue_analysis = await ProactiveGrowthService._analyze_revenue(
            db, workspace_id, current_period_start, previous_period_start, previous_period_end
        )
        
        # Analyze campaign performance
        campaign_analysis = await ProactiveGrowthService._analyze_campaigns(
            db, workspace_id, current_period_start, previous_period_start, previous_period_end
        )
        
        # Calculate overall health score
        health_score = ProactiveGrowthService._calculate_health_score(
            leads_analysis, revenue_analysis, campaign_analysis
        )
        
        # Detect alerts
        alerts = ProactiveGrowthService._detect_alerts(
            leads_analysis, revenue_analysis, campaign_analysis
        )
        
        return {
            "analysisDate": now.isoformat(),
            "healthScore": health_score,
            "leads": leads_analysis,
            "revenue": revenue_analysis,
            "campaigns": campaign_analysis,
            "alerts": alerts,
            "status": "healthy" if health_score >= 70 else "warning" if health_score >= 40 else "critical"
        }
    
    @staticmethod
    async def _analyze_leads(db, workspace_id: str, current_start, prev_start, prev_end) -> dict:
        """Analyze lead trends"""
        # Current period leads
        current_leads = await db.leads.count_documents({
            "workspace_id": workspace_id,
            "created_at": {"$gte": current_start.isoformat()}
        })
        
        # Previous period leads
        prev_leads = await db.leads.count_documents({
            "workspace_id": workspace_id,
            "created_at": {
                "$gte": prev_start.isoformat(),
                "$lt": prev_end.isoformat()
            }
        })
        
        # Conversion rate (leads that became CONVERTED)
        current_converted = await db.leads.count_documents({
            "workspace_id": workspace_id,
            "status": "CONVERTED",
            "created_at": {"$gte": current_start.isoformat()}
        })
        
        prev_converted = await db.leads.count_documents({
            "workspace_id": workspace_id,
            "status": "CONVERTED",
            "created_at": {
                "$gte": prev_start.isoformat(),
                "$lt": prev_end.isoformat()
            }
        })
        
        current_rate = (current_converted / current_leads * 100) if current_leads > 0 else 0
        prev_rate = (prev_converted / prev_leads * 100) if prev_leads > 0 else 0
        
        lead_change = ((current_leads - prev_leads) / prev_leads * 100) if prev_leads > 0 else 0
        rate_change = current_rate - prev_rate
        
        return {
            "currentPeriod": current_leads,
            "previousPeriod": prev_leads,
            "percentChange": round(lead_change, 1),
            "conversionRate": round(current_rate, 1),
            "conversionChange": round(rate_change, 1),
            "trend": "up" if lead_change > 0 else "down" if lead_change < 0 else "stable"
        }
    
    @staticmethod
    async def _analyze_revenue(db, workspace_id: str, current_start, prev_start, prev_end) -> dict:
        """Analyze revenue trends from invoices"""
        # Current period invoices
        current_invoices = await db.invoices.find({
            "workspace_id": workspace_id,
            "createdAt": {"$gte": current_start.isoformat()}
        }).to_list(length=1000)
        
        # Previous period invoices
        prev_invoices = await db.invoices.find({
            "workspace_id": workspace_id,
            "createdAt": {
                "$gte": prev_start.isoformat(),
                "$lt": prev_end.isoformat()
            }
        }).to_list(length=1000)
        
        current_revenue = sum(inv.get("totalAmount", 0) for inv in current_invoices)
        prev_revenue = sum(inv.get("totalAmount", 0) for inv in prev_invoices)
        
        current_paid = sum(1 for inv in current_invoices if inv.get("status") == "paid")
        
        revenue_change = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            "currentRevenue": round(current_revenue, 2),
            "previousRevenue": round(prev_revenue, 2),
            "percentChange": round(revenue_change, 1),
            "invoiceCount": len(current_invoices),
            "paidInvoices": current_paid,
            "trend": "up" if revenue_change > 0 else "down" if revenue_change < 0 else "stable"
        }
    
    @staticmethod
    async def _analyze_campaigns(db, workspace_id: str, current_start, prev_start, prev_end) -> dict:
        """Analyze marketing campaign performance"""
        # Active campaigns
        active_campaigns = await db.campaigns.count_documents({
            "workspace_id": workspace_id,
            "status": "active"
        })
        
        # Get campaign metrics
        all_campaigns = await db.campaigns.find({
            "workspace_id": workspace_id
        }).to_list(length=100)
        
        total_budget = sum(c.get("budget", 0) or 0 for c in all_campaigns)
        total_conversions = sum(c.get("metrics", {}).get("conversions", 0) for c in all_campaigns)
        total_clicks = sum(c.get("metrics", {}).get("clicks", 0) for c in all_campaigns)
        
        avg_ctr = 0
        campaigns_with_metrics = [c for c in all_campaigns if c.get("metrics", {}).get("impressions", 0) > 0]
        if campaigns_with_metrics:
            avg_ctr = sum(c.get("metrics", {}).get("ctr", 0) for c in campaigns_with_metrics) / len(campaigns_with_metrics)
        
        return {
            "activeCampaigns": active_campaigns,
            "totalCampaigns": len(all_campaigns),
            "totalBudget": round(total_budget, 2),
            "totalConversions": total_conversions,
            "totalClicks": total_clicks,
            "averageCTR": round(avg_ctr, 2),
            "trend": "up" if active_campaigns > 0 and total_conversions > 0 else "stable"
        }
    
    @staticmethod
    def _calculate_health_score(leads: dict, revenue: dict, campaigns: dict) -> int:
        """Calculate overall business health score (0-100)"""
        score = 50  # Base score
        
        # Lead metrics (up to 25 points)
        if leads["percentChange"] > 10:
            score += 15
        elif leads["percentChange"] > 0:
            score += 10
        elif leads["percentChange"] > -10:
            score += 5
        else:
            score -= 10
        
        if leads["conversionRate"] > 15:
            score += 10
        elif leads["conversionRate"] > 5:
            score += 5
        
        # Revenue metrics (up to 25 points)
        if revenue["percentChange"] > 10:
            score += 15
        elif revenue["percentChange"] > 0:
            score += 10
        elif revenue["percentChange"] > -10:
            score += 5
        else:
            score -= 10
        
        if revenue["paidInvoices"] > 0:
            score += 10
        
        # Campaign activity (up to 10 points)
        if campaigns["activeCampaigns"] >= 2:
            score += 10
        elif campaigns["activeCampaigns"] >= 1:
            score += 5
        
        return max(0, min(100, score))
    
    @staticmethod
    def _detect_alerts(leads: dict, revenue: dict, campaigns: dict) -> List[dict]:
        """Detect business alerts that need attention"""
        alerts = []
        
        # Lead decline alert
        if leads["percentChange"] < -20:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "lead_decline",
                "severity": "critical",
                "title": "Significant Lead Decline",
                "message": f"Leads have dropped by {abs(leads['percentChange'])}% compared to last month",
                "suggestedAction": "marketing_campaign",
                "actionLabel": "Launch Marketing Campaign"
            })
        elif leads["percentChange"] < -10:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "lead_decline",
                "severity": "warning",
                "title": "Lead Generation Slowdown",
                "message": f"Leads have decreased by {abs(leads['percentChange'])}%",
                "suggestedAction": "social_campaign",
                "actionLabel": "Boost Social Presence"
            })
        
        # Conversion rate decline
        if leads["conversionChange"] < -5:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "conversion_decline",
                "severity": "warning",
                "title": "Conversion Rate Drop",
                "message": f"Conversion rate has dropped by {abs(leads['conversionChange'])}%",
                "suggestedAction": "lead_nurture",
                "actionLabel": "Improve Lead Nurturing"
            })
        
        # Revenue decline alert
        if revenue["percentChange"] < -10:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "revenue_decline",
                "severity": "critical",
                "title": "Revenue Decline Detected",
                "message": f"Revenue has dropped by {abs(revenue['percentChange'])}% this month",
                "suggestedAction": "sales_campaign",
                "actionLabel": "Launch Sales Initiative"
            })
        
        # No active campaigns
        if campaigns["activeCampaigns"] == 0:
            alerts.append({
                "id": str(uuid.uuid4()),
                "type": "no_campaigns",
                "severity": "info",
                "title": "No Active Marketing",
                "message": "You have no active marketing campaigns running",
                "suggestedAction": "create_campaign",
                "actionLabel": "Create Campaign"
            })
        
        return alerts
    
    @staticmethod
    async def generate_growth_recommendation(
        workspace_id: str,
        alert_type: str,
        company_profile: Optional[dict] = None
    ) -> dict:
        """
        Generate AI-powered growth recommendation based on alert type.
        Returns a proposed action plan for user approval.
        """
        db = get_db()
        
        # Get business context
        profile = company_profile
        if not profile:
            profile = await db.company_profiles.find_one(
                {"workspace_id": workspace_id},
                {"_id": 0}
            )
        
        business_name = profile.get("legalName", "Your Business") if profile else "Your Business"
        industry = profile.get("officialProfile", {}).get("companyType", "Business") if profile else "Business"
        
        # Generate recommendation based on alert type
        recommendation = await ProactiveGrowthService._get_recommendation_for_alert(
            alert_type, business_name, industry, workspace_id
        )
        
        # Store recommendation for approval
        recommendation_id = str(uuid.uuid4())
        recommendation_doc = {
            "id": recommendation_id,
            "workspace_id": workspace_id,
            "alertType": alert_type,
            "recommendation": recommendation,
            "status": "pending",  # pending, approved, rejected
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        await db.growth_recommendations.insert_one(recommendation_doc)
        
        return {
            "id": recommendation_id,
            **recommendation,
            "status": "pending"
        }
    
    @staticmethod
    async def _get_recommendation_for_alert(
        alert_type: str,
        business_name: str,
        industry: str,
        workspace_id: str
    ) -> dict:
        """Generate specific recommendation based on alert type"""
        
        recommendations = {
            "lead_decline": {
                "title": "Lead Generation Campaign",
                "type": "marketing_campaign",
                "description": f"Launch a targeted campaign to increase lead generation for {business_name}",
                "actions": [
                    {
                        "type": "social_post",
                        "platform": "linkedin",
                        "content": None,  # Will be generated
                        "schedule": "immediate"
                    },
                    {
                        "type": "email_campaign",
                        "target": "cold_leads",
                        "template": "re-engagement"
                    }
                ],
                "expectedOutcome": "15-25% increase in lead generation",
                "estimatedBudget": 0,
                "duration": "2 weeks"
            },
            "conversion_decline": {
                "title": "Lead Nurturing Optimization",
                "type": "nurture_campaign",
                "description": "Improve conversion rates with better follow-up sequences",
                "actions": [
                    {
                        "type": "email_sequence",
                        "target": "qualified_leads",
                        "template": "nurture"
                    },
                    {
                        "type": "content_creation",
                        "content_type": "case_study"
                    }
                ],
                "expectedOutcome": "5-10% improvement in conversion rate",
                "estimatedBudget": 0,
                "duration": "1 month"
            },
            "revenue_decline": {
                "title": "Revenue Recovery Campaign",
                "type": "sales_initiative",
                "description": "Targeted sales campaign to boost revenue",
                "actions": [
                    {
                        "type": "promotion",
                        "discount": "10%",
                        "duration": "1 week"
                    },
                    {
                        "type": "upsell_campaign",
                        "target": "existing_customers"
                    }
                ],
                "expectedOutcome": "10-20% revenue increase",
                "estimatedBudget": 0,
                "duration": "2 weeks"
            },
            "no_campaigns": {
                "title": "Quick Win Marketing",
                "type": "starter_campaign",
                "description": "Get started with basic marketing activities",
                "actions": [
                    {
                        "type": "social_post",
                        "platform": "all",
                        "frequency": "3x per week"
                    }
                ],
                "expectedOutcome": "Establish marketing presence",
                "estimatedBudget": 0,
                "duration": "ongoing"
            }
        }
        
        base_rec = recommendations.get(alert_type, recommendations["no_campaigns"])
        
        # Generate AI content if available
        if LLM_AVAILABLE and alert_type in ["lead_decline", "no_campaigns"]:
            ai_content = await ProactiveGrowthService._generate_ai_content(
                business_name, industry, alert_type
            )
            if ai_content and base_rec.get("actions"):
                for action in base_rec["actions"]:
                    if action.get("type") == "social_post":
                        action["content"] = ai_content
        
        return base_rec
    
    @staticmethod
    async def _generate_ai_content(business_name: str, industry: str, alert_type: str) -> Optional[str]:
        """Generate AI content for recommended actions"""
        if not LLM_AVAILABLE:
            return None
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return None
            
            chat = LlmChat(
                api_key=llm_key,
                session_id=f"growth-agent-{uuid.uuid4().hex[:8]}",
                system_message="""You are a marketing expert. Generate compelling, professional 
                social media content for business growth. Keep posts concise, engaging, and 
                suitable for LinkedIn/Twitter. Include a clear call-to-action."""
            ).with_model("openai", "gpt-4o")
            
            prompt = f"""Generate a professional social media post for {business_name}, 
            a company in the {industry} industry. The goal is to increase lead generation 
            and brand awareness. Make it engaging, professional, and include relevant hashtags."""
            
            response = await chat.send_message(UserMessage(text=prompt))
            return response.text if hasattr(response, 'text') else str(response)
            
        except Exception as e:
            print(f"AI content generation error: {e}")
            return None
    
    @staticmethod
    async def approve_recommendation(
        recommendation_id: str,
        workspace_id: str,
        user_id: str
    ) -> dict:
        """Approve and execute a growth recommendation"""
        db = get_db()
        
        rec = await db.growth_recommendations.find_one({
            "id": recommendation_id,
            "workspace_id": workspace_id
        })
        
        if not rec:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        if rec.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Recommendation already processed")
        
        # Execute the recommendation actions
        executed_actions = []
        recommendation = rec.get("recommendation", {})
        
        for action in recommendation.get("actions", []):
            action_result = await ProactiveGrowthService._execute_action(
                action, workspace_id, user_id
            )
            executed_actions.append(action_result)
        
        # Update recommendation status
        await db.growth_recommendations.update_one(
            {"id": recommendation_id},
            {
                "$set": {
                    "status": "approved",
                    "approvedAt": datetime.now(timezone.utc).isoformat(),
                    "approvedBy": user_id,
                    "executedActions": executed_actions
                }
            }
        )
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "growth.recommendation_approved",
            "data": {"recommendation_id": recommendation_id},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "id": recommendation_id,
            "status": "approved",
            "executedActions": executed_actions,
            "message": "Growth recommendation approved and executed"
        }
    
    @staticmethod
    async def _execute_action(action: dict, workspace_id: str, user_id: str) -> dict:
        """Execute a specific growth action"""
        db = get_db()
        action_type = action.get("type")
        
        if action_type == "social_post":
            # Create social post
            post_id = str(uuid.uuid4())
            post = {
                "id": post_id,
                "workspace_id": workspace_id,
                "platform": action.get("platform", "linkedin"),
                "content": action.get("content", "Check out our latest updates!"),
                "hashtags": ["business", "growth"],
                "status": "draft",
                "scheduledFor": None,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "createdBy": user_id,
                "source": "growth_agent"
            }
            await db.social_posts.insert_one(post)
            return {"type": "social_post", "id": post_id, "status": "created"}
        
        elif action_type == "email_campaign":
            # Log email campaign intent (actual sending requires user setup)
            return {
                "type": "email_campaign",
                "status": "queued",
                "target": action.get("target"),
                "message": "Email campaign queued for setup"
            }
        
        elif action_type == "promotion":
            # Log promotion intent
            return {
                "type": "promotion",
                "status": "suggested",
                "discount": action.get("discount"),
                "message": "Promotion strategy suggested - implement via your sales channels"
            }
        
        return {"type": action_type, "status": "acknowledged"}
    
    @staticmethod
    async def reject_recommendation(
        recommendation_id: str,
        workspace_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> dict:
        """Reject a growth recommendation"""
        db = get_db()
        
        rec = await db.growth_recommendations.find_one({
            "id": recommendation_id,
            "workspace_id": workspace_id
        })
        
        if not rec:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        await db.growth_recommendations.update_one(
            {"id": recommendation_id},
            {
                "$set": {
                    "status": "rejected",
                    "rejectedAt": datetime.now(timezone.utc).isoformat(),
                    "rejectedBy": user_id,
                    "rejectionReason": reason
                }
            }
        )
        
        return {
            "id": recommendation_id,
            "status": "rejected",
            "message": "Recommendation rejected"
        }
    
    @staticmethod
    async def get_recommendations(workspace_id: str, status: Optional[str] = None) -> List[dict]:
        """Get all growth recommendations for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if status:
            query["status"] = status
        
        recs = await db.growth_recommendations.find(query).sort("createdAt", -1).to_list(length=50)
        return [{k: v for k, v in rec.items() if k != '_id'} for rec in recs]
