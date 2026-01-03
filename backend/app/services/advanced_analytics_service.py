"""Advanced Analytics Service - Comprehensive business intelligence"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from app.core.database import get_db


class AdvancedAnalyticsService:
    """
    Service for advanced business analytics and reporting.
    Provides deep insights into business performance across all modules.
    """
    
    @staticmethod
    async def get_dashboard_overview(workspace_id: str) -> dict:
        """Get comprehensive dashboard overview"""
        db = get_db()
        now = datetime.now(timezone.utc)
        
        # Get all relevant data
        leads = await db.leads.find({"workspace_id": workspace_id}).to_list(length=5000)
        campaigns = await db.campaigns.find({"workspace_id": workspace_id}).to_list(length=500)
        invoices = await db.invoices.find({"workspace_id": workspace_id}).to_list(length=5000)
        expenses = await db.expenses.find({"workspace_id": workspace_id}).to_list(length=5000)
        social_posts = await db.social_posts.find({"workspace_id": workspace_id}).to_list(length=1000)
        
        # Calculate metrics
        total_revenue = sum(inv.get("totalAmount", 0) for inv in invoices if inv.get("status") == "paid")
        total_expenses = sum(exp.get("amount", 0) for exp in expenses)
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Lead metrics
        converted_leads = len([lead for lead in leads if lead.get("status") == "CONVERTED"])
        conversion_rate = (converted_leads / len(leads) * 100) if leads else 0
        
        # Campaign metrics
        active_campaigns = len([c for c in campaigns if c.get("status") == "active"])
        total_campaign_spend = sum(c.get("metrics", {}).get("spend", 0) for c in campaigns)
        total_conversions = sum(c.get("metrics", {}).get("conversions", 0) for c in campaigns)
        
        # Social metrics
        published_posts = len([p for p in social_posts if p.get("status") == "published"])
        scheduled_posts = len([p for p in social_posts if p.get("status") == "scheduled"])
        
        return {
            "overview": {
                "totalRevenue": round(total_revenue, 2),
                "totalExpenses": round(total_expenses, 2),
                "netProfit": round(net_profit, 2),
                "profitMargin": round(profit_margin, 1)
            },
            "growth": {
                "totalLeads": len(leads),
                "convertedLeads": converted_leads,
                "conversionRate": round(conversion_rate, 1),
                "activeCampaigns": active_campaigns,
                "totalCampaigns": len(campaigns),
                "campaignSpend": round(total_campaign_spend, 2),
                "totalConversions": total_conversions
            },
            "social": {
                "totalPosts": len(social_posts),
                "publishedPosts": published_posts,
                "scheduledPosts": scheduled_posts,
                "platformBreakdown": AdvancedAnalyticsService._get_platform_breakdown(social_posts)
            },
            "finance": {
                "totalInvoices": len(invoices),
                "paidInvoices": len([i for i in invoices if i.get("status") == "paid"]),
                "pendingInvoices": len([i for i in invoices if i.get("status") == "pending"]),
                "overdueInvoices": len([i for i in invoices if i.get("status") == "overdue"]),
                "avgInvoiceValue": round(total_revenue / len(invoices), 2) if invoices else 0
            },
            "generatedAt": now.isoformat()
        }
    
    @staticmethod
    def _get_platform_breakdown(posts: List[dict]) -> dict:
        """Get breakdown by social platform"""
        breakdown = {}
        for post in posts:
            platform = post.get("platform", "other")
            breakdown[platform] = breakdown.get(platform, 0) + 1
        return breakdown
    
    @staticmethod
    async def get_revenue_trends(workspace_id: str, days: int = 30) -> dict:
        """Get revenue trends over time"""
        db = get_db()
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)
        
        invoices = await db.invoices.find({
            "workspace_id": workspace_id,
            "createdAt": {"$gte": start_date.isoformat()}
        }).to_list(length=5000)
        
        expenses = await db.expenses.find({
            "workspace_id": workspace_id,
            "createdAt": {"$gte": start_date.isoformat()}
        }).to_list(length=5000)
        
        # Group by date
        daily_data = {}
        for i in range(days + 1):
            date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_data[date] = {"revenue": 0, "expenses": 0, "profit": 0}
        
        for inv in invoices:
            if inv.get("status") == "paid":
                date = inv.get("createdAt", "")[:10]
                if date in daily_data:
                    daily_data[date]["revenue"] += inv.get("totalAmount", 0)
        
        for exp in expenses:
            date = exp.get("createdAt", "")[:10]
            if date in daily_data:
                daily_data[date]["expenses"] += exp.get("amount", 0)
        
        # Calculate profits
        for date in daily_data:
            daily_data[date]["profit"] = daily_data[date]["revenue"] - daily_data[date]["expenses"]
        
        # Convert to list sorted by date
        trend_data = [
            {
                "date": date,
                "revenue": round(data["revenue"], 2),
                "expenses": round(data["expenses"], 2),
                "profit": round(data["profit"], 2)
            }
            for date, data in sorted(daily_data.items())
        ]
        
        # Calculate summary
        total_revenue = sum(d["revenue"] for d in trend_data)
        total_expenses = sum(d["expenses"] for d in trend_data)
        total_profit = total_revenue - total_expenses
        
        return {
            "period": f"{days} days",
            "trends": trend_data,
            "summary": {
                "totalRevenue": round(total_revenue, 2),
                "totalExpenses": round(total_expenses, 2),
                "totalProfit": round(total_profit, 2),
                "avgDailyRevenue": round(total_revenue / days, 2),
                "avgDailyExpenses": round(total_expenses / days, 2)
            }
        }
    
    @staticmethod
    async def get_lead_funnel(workspace_id: str) -> dict:
        """Get lead funnel analytics"""
        db = get_db()
        
        leads = await db.leads.find({"workspace_id": workspace_id}).to_list(length=5000)
        
        funnel = {
            "NEW": 0,
            "CONTACTED": 0,
            "QUALIFIED": 0,
            "CONVERTED": 0,
            "LOST": 0
        }
        
        source_breakdown = {}
        
        for lead in leads:
            status = lead.get("status", "NEW")
            source = lead.get("source", "OTHER")
            
            funnel[status] = funnel.get(status, 0) + 1
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        total = len(leads)
        
        # Calculate funnel percentages
        funnel_rates = {}
        for status, count in funnel.items():
            funnel_rates[status] = round((count / total * 100) if total > 0 else 0, 1)
        
        # Calculate stage-to-stage conversion
        stage_conversion = {
            "new_to_contacted": round((funnel["CONTACTED"] / funnel["NEW"] * 100) if funnel["NEW"] > 0 else 0, 1),
            "contacted_to_qualified": round((funnel["QUALIFIED"] / funnel["CONTACTED"] * 100) if funnel["CONTACTED"] > 0 else 0, 1),
            "qualified_to_converted": round((funnel["CONVERTED"] / funnel["QUALIFIED"] * 100) if funnel["QUALIFIED"] > 0 else 0, 1),
        }
        
        return {
            "total": total,
            "funnel": funnel,
            "funnelRates": funnel_rates,
            "stageConversion": stage_conversion,
            "sourceBreakdown": source_breakdown,
            "overallConversionRate": funnel_rates.get("CONVERTED", 0)
        }
    
    @staticmethod
    async def get_campaign_performance(workspace_id: str) -> dict:
        """Get detailed campaign performance analytics"""
        db = get_db()
        
        campaigns = await db.campaigns.find({"workspace_id": workspace_id}).to_list(length=500)
        
        if not campaigns:
            return {
                "totalCampaigns": 0,
                "activeCount": 0,
                "summary": {},
                "topPerformers": [],
                "channelBreakdown": {}
            }
        
        # Aggregate metrics
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_spend = 0
        total_budget = 0
        
        by_status = {}
        by_type = {}
        by_channel = {}
        
        for c in campaigns:
            metrics = c.get("metrics", {})
            total_impressions += metrics.get("impressions", 0)
            total_clicks += metrics.get("clicks", 0)
            total_conversions += metrics.get("conversions", 0)
            total_spend += metrics.get("spend", 0)
            total_budget += c.get("budget", 0) or 0
            
            status = c.get("status", "draft")
            by_status[status] = by_status.get(status, 0) + 1
            
            ctype = c.get("type", "other")
            by_type[ctype] = by_type.get(ctype, 0) + 1
            
            for channel in c.get("channels", []):
                by_channel[channel] = by_channel.get(channel, 0) + 1
        
        # Calculate rates
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpc = total_spend / total_clicks if total_clicks > 0 else 0
        cpa = total_spend / total_conversions if total_conversions > 0 else 0
        
        # Top performers by conversions
        sorted_campaigns = sorted(
            campaigns,
            key=lambda c: c.get("metrics", {}).get("conversions", 0),
            reverse=True
        )[:10]
        
        top_performers = [
            {
                "id": c["id"],
                "name": c["name"],
                "type": c.get("type"),
                "status": c.get("status"),
                "conversions": c.get("metrics", {}).get("conversions", 0),
                "spend": c.get("metrics", {}).get("spend", 0),
                "roi": c.get("metrics", {}).get("roi", 0)
            }
            for c in sorted_campaigns
        ]
        
        return {
            "totalCampaigns": len(campaigns),
            "activeCount": by_status.get("active", 0),
            "summary": {
                "totalImpressions": total_impressions,
                "totalClicks": total_clicks,
                "totalConversions": total_conversions,
                "totalSpend": round(total_spend, 2),
                "totalBudget": round(total_budget, 2),
                "budgetUtilization": round((total_spend / total_budget * 100) if total_budget > 0 else 0, 1),
                "ctr": round(ctr, 2),
                "conversionRate": round(conversion_rate, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2)
            },
            "byStatus": by_status,
            "byType": by_type,
            "channelBreakdown": by_channel,
            "topPerformers": top_performers
        }
    
    @staticmethod
    async def get_social_analytics(workspace_id: str, days: int = 30) -> dict:
        """Get social media analytics"""
        db = get_db()
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)
        
        posts = await db.social_posts.find({
            "workspace_id": workspace_id,
            "createdAt": {"$gte": start_date.isoformat()}
        }).to_list(length=1000)
        
        # Platform breakdown
        by_platform = {}
        by_status = {}
        posts_by_day = {}
        
        for post in posts:
            platform = post.get("platform", "other")
            status = post.get("status", "draft")
            
            by_platform[platform] = by_platform.get(platform, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
            
            date = post.get("createdAt", "")[:10]
            if date:
                posts_by_day[date] = posts_by_day.get(date, 0) + 1
        
        # Calculate posting frequency
        avg_posts_per_day = len(posts) / days if days > 0 else 0
        
        return {
            "totalPosts": len(posts),
            "period": f"{days} days",
            "byPlatform": by_platform,
            "byStatus": by_status,
            "postsPerDay": round(avg_posts_per_day, 2),
            "dailyActivity": [
                {"date": date, "posts": count}
                for date, count in sorted(posts_by_day.items())
            ],
            "platformRecommendations": AdvancedAnalyticsService._get_platform_recommendations(by_platform)
        }
    
    @staticmethod
    def _get_platform_recommendations(by_platform: dict) -> List[dict]:
        """Get platform-specific recommendations"""
        recommendations = []
        
        platforms = ["linkedin", "twitter", "facebook", "instagram"]
        for platform in platforms:
            count = by_platform.get(platform, 0)
            if count == 0:
                recommendations.append({
                    "platform": platform,
                    "type": "missing",
                    "message": f"You have no posts on {platform.title()}. Consider expanding your presence."
                })
            elif count < 5:
                recommendations.append({
                    "platform": platform,
                    "type": "low_activity",
                    "message": f"Your {platform.title()} activity is low. Try posting more frequently."
                })
        
        return recommendations
    
    @staticmethod
    async def generate_business_report(workspace_id: str, report_type: str = "monthly") -> dict:
        """Generate a comprehensive business report"""
        now = datetime.now(timezone.utc)
        
        days = 30 if report_type == "monthly" else 7 if report_type == "weekly" else 90
        start_date = now - timedelta(days=days)
        
        # Gather all metrics
        dashboard = await AdvancedAnalyticsService.get_dashboard_overview(workspace_id)
        revenue_trends = await AdvancedAnalyticsService.get_revenue_trends(workspace_id, days)
        lead_funnel = await AdvancedAnalyticsService.get_lead_funnel(workspace_id)
        campaign_perf = await AdvancedAnalyticsService.get_campaign_performance(workspace_id)
        social_analytics = await AdvancedAnalyticsService.get_social_analytics(workspace_id, days)
        
        # Generate insights
        insights = AdvancedAnalyticsService._generate_insights(
            dashboard, revenue_trends, lead_funnel, campaign_perf
        )
        
        return {
            "reportType": report_type,
            "period": {
                "start": start_date.isoformat(),
                "end": now.isoformat(),
                "days": days
            },
            "generatedAt": now.isoformat(),
            "executiveSummary": {
                "revenue": dashboard["overview"]["totalRevenue"],
                "profit": dashboard["overview"]["netProfit"],
                "leads": dashboard["growth"]["totalLeads"],
                "conversionRate": lead_funnel["overallConversionRate"],
                "activeCampaigns": campaign_perf["activeCount"]
            },
            "sections": {
                "financial": revenue_trends,
                "leads": lead_funnel,
                "campaigns": campaign_perf,
                "social": social_analytics
            },
            "insights": insights,
            "recommendations": AdvancedAnalyticsService._generate_recommendations(
                dashboard, lead_funnel, campaign_perf, social_analytics
            )
        }
    
    @staticmethod
    def _generate_insights(dashboard: dict, revenue: dict, funnel: dict, campaigns: dict) -> List[dict]:
        """Generate actionable insights from data"""
        insights = []
        
        # Revenue insight
        profit_margin = dashboard["overview"]["profitMargin"]
        if profit_margin > 30:
            insights.append({
                "type": "positive",
                "category": "finance",
                "title": "Strong Profit Margin",
                "message": f"Your profit margin of {profit_margin}% is excellent."
            })
        elif profit_margin < 10:
            insights.append({
                "type": "warning",
                "category": "finance",
                "title": "Low Profit Margin",
                "message": f"Your profit margin of {profit_margin}% could be improved. Review expenses."
            })
        
        # Conversion insight
        conversion_rate = funnel["overallConversionRate"]
        if conversion_rate > 20:
            insights.append({
                "type": "positive",
                "category": "growth",
                "title": "High Conversion Rate",
                "message": f"Your {conversion_rate}% conversion rate is above industry average."
            })
        elif conversion_rate < 5:
            insights.append({
                "type": "warning",
                "category": "growth",
                "title": "Low Conversion Rate",
                "message": "Consider reviewing your sales process to improve conversions."
            })
        
        # Campaign insight
        if campaigns["activeCount"] == 0:
            insights.append({
                "type": "action",
                "category": "marketing",
                "title": "No Active Campaigns",
                "message": "Launch a campaign to drive more leads and growth."
            })
        
        return insights
    
    @staticmethod
    def _generate_recommendations(dashboard: dict, funnel: dict, campaigns: dict, social: dict) -> List[dict]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Lead recommendations
        if funnel["total"] < 10:
            recommendations.append({
                "priority": "high",
                "category": "growth",
                "action": "Increase lead generation",
                "description": "Your lead count is low. Focus on content marketing and paid acquisition."
            })
        
        # Campaign recommendations
        if campaigns["activeCount"] == 0:
            recommendations.append({
                "priority": "high",
                "category": "marketing",
                "action": "Launch marketing campaigns",
                "description": "Start with social media campaigns to boost brand awareness."
            })
        
        # Social recommendations
        if social["totalPosts"] < 5:
            recommendations.append({
                "priority": "medium",
                "category": "social",
                "action": "Increase social media activity",
                "description": "Post regularly to maintain audience engagement."
            })
        
        # Platform-specific
        for rec in social.get("platformRecommendations", []):
            recommendations.append({
                "priority": "low",
                "category": "social",
                "action": f"Expand {rec['platform'].title()} presence",
                "description": rec["message"]
            })
        
        return recommendations
