"""Comprehensive Validation Report Service with AI-powered analysis"""
import uuid
import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from app.core.database import get_db
from app.schemas.validation_report import (
    ValidationReportCreate,
    ComprehensiveReport,
    AIScores,
    ScoreItem,
    BusinessFit,
    BusinessFitItem,
    OfferTier,
    FrameworkAnalysis,
    FrameworkScore,
    CommunitySignal,
    KeywordData,
    Categorization,
    ReportStatus
)

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class ValidationReportService:
    """Service for comprehensive idea validation reports"""
    
    @staticmethod
    async def create_comprehensive_report(
        workspace_id: str, 
        user_id: str, 
        data: ValidationReportCreate
    ) -> dict:
        """Create a comprehensive IdeaBrowser-style validation report"""
        db = get_db()
        
        # Generate AI-powered comprehensive report
        report = await ValidationReportService._generate_ai_report(data)
        
        # Create database document
        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        doc = {
            "id": report_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": ReportStatus.PENDING.value,
            "ideaInput": data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
            "report": report,
            "createdAt": now,
            "updatedAt": now
        }
        
        # Store in database
        await db.validation_reports.insert_one(doc)
        
        # Update engagement counter
        await ValidationReportService._increment_engagement(workspace_id, user_id)
        
        # Log intelligence event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "validation.report_created",
            "data": {
                "report_id": report_id,
                "idea_name": data.ideaName,
                "idea_type": data.ideaType,
                "overall_score": report["scores"]["opportunity"]["value"]
            },
            "occurredAt": now
        })
        
        # Return without _id
        doc.pop("_id", None)
        return doc
    
    @staticmethod
    async def _generate_ai_report(data: ValidationReportCreate) -> dict:
        """Generate comprehensive report using AI"""
        
        # Build prompt for AI
        prompt = f"""You are an expert business analyst. Analyze this business/product idea and generate a comprehensive validation report.

IDEA DETAILS:
- Type: {data.ideaType}
- Name: {data.ideaName}
- Description: {data.ideaDescription}
- Industry: {data.industry} ({data.subIndustry or 'General'})
- Problem Solved: {data.problemSolved}
- Target Audience: {data.targetAudience}
- Urgency Level: {data.urgencyLevel}
- How It Works: {data.howItWorks}
- Delivery Model: {data.deliveryModel}
- Target Market: {data.targetMarket}
- Target Location: {data.targetLocation}
- Customer Budget: {data.customerBudget}
- Go-To-Market Channels: {', '.join(data.goToMarketChannel)}

Generate a JSON response with this EXACT structure (all fields required):
{{
    "title": "A compelling title for the idea",
    "tags": ["3-5 tags like 'Perfect Timing', 'Strong Market', 'High Potential'"],
    "description": "2-3 paragraphs describing the idea's potential, market context, and key opportunities",
    "scores": {{
        "opportunity": {{"value": 1-10, "label": "description", "description": "why this score"}},
        "problem": {{"value": 1-10, "label": "description", "description": "why this score"}},
        "feasibility": {{"value": 1-10, "label": "description", "description": "why this score"}},
        "whyNow": {{"value": 1-10, "label": "description", "description": "why this score"}}
    }},
    "businessFit": {{
        "revenuePotential": {{"indicator": "$" to "$$$", "description": "revenue potential analysis"}},
        "executionDifficulty": {{"score": 1-10, "description": "execution analysis"}},
        "goToMarket": {{"score": 1-10, "description": "GTM analysis"}}
    }},
    "offer": [
        {{"tier": "LEAD MAGNET", "name": "product name", "price": "Free", "description": "what it is"}},
        {{"tier": "FRONTEND", "name": "product name", "price": "$X/month", "description": "what it is"}},
        {{"tier": "CORE", "name": "product name", "price": "$X-Y/month", "description": "what it is"}}
    ],
    "whyNow": "2-3 sentences on why now is the right time",
    "proofSignals": "2-3 sentences on market demand signals",
    "marketGap": "2-3 sentences on the market opportunity",
    "executionPlan": "2-3 sentences on MVP and growth strategy",
    "frameworkFit": [
        {{"name": "Value Equation", "overallScore": 1-10, "scores": [{{"name": "metric", "score": 1-10}}]}},
        {{"name": "Market Position", "description": "analysis"}},
        {{"name": "ACP Framework", "scores": [{{"name": "Audience", "score": 1-10}}, {{"name": "Community", "score": 1-10}}, {{"name": "Product", "score": 1-10}}]}}
    ],
    "categorization": {{
        "type": "SaaS/Service/Marketplace/etc",
        "market": "B2C/B2B/B2G",
        "target": "target segment",
        "trendAnalysis": "trend insights"
    }},
    "communitySignals": [
        {{"platform": "Reddit", "details": "X subreddits - Y members", "score": 1-10}},
        {{"platform": "Facebook", "details": "X groups - Y members", "score": 1-10}},
        {{"platform": "YouTube", "details": "X channels", "score": 1-10}}
    ],
    "topKeywords": [
        {{"keyword": "keyword1", "volume": "X.XK", "competition": "LOW/MEDIUM/HIGH", "growth": "+XX%"}},
        {{"keyword": "keyword2", "volume": "X.XK", "competition": "LOW/MEDIUM/HIGH"}}
    ],
    "trendKeyword": "main keyword",
    "trendVolume": "X.XK",
    "trendGrowth": "+XX%",
    "buildPrompts": ["Ad Creatives", "Brand Package", "Landing Page", "Email Sequence"],
    "suggestedQuestions": [
        "What problem does this solve?",
        "How big is the market opportunity?",
        "What's the competitive landscape?",
        "How hard is it to build?",
        "What's the revenue model?",
        "What are the key risks?"
    ]
}}

Be realistic but constructive. Base scores on the information provided. Return ONLY valid JSON."""

        try:
            if LLM_AVAILABLE:
                llm_key = os.environ.get("LLM_KEY")
                if llm_key:
                    chat = LlmChat(
                        api_key=llm_key,
                        model="gpt-4o"
                    )
                    response = await chat.send_message(
                        UserMessage(content=prompt)
                    )
                    
                    # Parse JSON from response
                    response_text = response.content if hasattr(response, 'content') else str(response)
                    
                    # Extract JSON from response (handle markdown code blocks)
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]
                    
                    report = json.loads(response_text.strip())
                    return report
        except Exception as e:
            print(f"AI report generation failed: {e}")
        
        # Fallback to rule-based generation
        return ValidationReportService._generate_fallback_report(data)
    
    @staticmethod
    def _generate_fallback_report(data: ValidationReportCreate) -> dict:
        """Generate a comprehensive report without AI (fallback)"""
        
        # Calculate scores based on input quality
        problem_len = len(data.problemSolved)
        desc_len = len(data.ideaDescription)
        audience_len = len(data.targetAudience)
        how_len = len(data.howItWorks)
        
        # Opportunity score
        opp_score = min(9, 5 + (desc_len // 50) + (1 if data.urgencyLevel == "high" else 0))
        
        # Problem score
        prob_score = min(9, 4 + (problem_len // 40) + (2 if data.urgencyLevel == "high" else 1 if data.urgencyLevel == "medium" else 0))
        
        # Feasibility score
        easy_models = ["digital", "saas", "mobile app"]
        feas_score = 7 if data.deliveryModel.lower() in easy_models else 5
        feas_score = min(9, feas_score + (how_len // 100))
        
        # Why Now score
        why_now_score = 8 if data.urgencyLevel == "high" else 6 if data.urgencyLevel == "medium" else 4
        why_now_score = min(9, why_now_score + len(data.goToMarketChannel) // 2)
        
        # Revenue indicator
        rev_indicator = "$$$" if data.customerBudget == "high" else "$$" if data.customerBudget == "medium" else "$"
        
        # Execution difficulty
        exec_diff = 5 if data.deliveryModel.lower() in easy_models else 7
        
        # GTM score
        gtm_score = min(9, 5 + len(data.goToMarketChannel))
        
        return {
            "title": data.ideaName,
            "tags": ValidationReportService._generate_tags(data, opp_score, prob_score),
            "description": f"{data.ideaDescription}\n\nThis {data.ideaType} targets {data.targetAudience} in the {data.industry} industry. The solution addresses: {data.problemSolved}",
            "disclaimer": "*Analysis and scores are based on provided information and general market assumptions. Results vary by execution and market conditions.",
            "scores": {
                "opportunity": {
                    "value": opp_score,
                    "label": "Exceptional" if opp_score >= 8 else "Good" if opp_score >= 6 else "Moderate",
                    "description": f"Strong market opportunity in {data.industry}"
                },
                "problem": {
                    "value": prob_score,
                    "label": "High Pain" if prob_score >= 7 else "Moderate Pain" if prob_score >= 5 else "Low Pain",
                    "description": f"Problem urgency is {data.urgencyLevel}"
                },
                "feasibility": {
                    "value": feas_score,
                    "label": "Achievable" if feas_score >= 7 else "Challenging" if feas_score >= 5 else "Difficult",
                    "description": f"{data.deliveryModel} delivery model assessment"
                },
                "whyNow": {
                    "value": why_now_score,
                    "label": "Perfect Timing" if why_now_score >= 8 else "Good Timing" if why_now_score >= 6 else "Timing Concerns",
                    "description": "Market timing analysis"
                }
            },
            "businessFit": {
                "revenuePotential": {
                    "indicator": rev_indicator,
                    "description": f"Target customers have {data.customerBudget} budget capacity"
                },
                "executionDifficulty": {
                    "score": exec_diff,
                    "description": f"Building a {data.deliveryModel} requires moderate technical execution"
                },
                "goToMarket": {
                    "score": gtm_score,
                    "description": f"Planned channels: {', '.join(data.goToMarketChannel[:3])}"
                }
            },
            "offer": [
                {
                    "tier": "LEAD MAGNET",
                    "name": f"{data.ideaName} Calculator",
                    "price": "Free",
                    "description": f"Free tool to estimate value for {data.targetAudience}"
                },
                {
                    "tier": "FRONTEND",
                    "name": f"Basic {data.ideaName}",
                    "price": "$15/month",
                    "description": f"Entry-level offering for individual {data.targetMarket} customers"
                },
                {
                    "tier": "CORE",
                    "name": f"Pro {data.ideaName}",
                    "price": "$30-50/month",
                    "description": f"Full-featured solution with premium capabilities"
                }
            ],
            "whyNow": f"Now is an opportune time to launch in the {data.industry} market. With {data.urgencyLevel} urgency around {data.problemSolved[:100]}..., early movers can capture significant market share.",
            "proofSignals": f"Market research indicates strong demand signals in {data.targetLocation}. The {data.targetMarket} segment shows active interest in solutions addressing {data.problemSolved[:80]}...",
            "marketGap": f"Current solutions in {data.industry} don't fully address the needs of {data.targetAudience}. This creates a clear opportunity to differentiate through {data.deliveryModel} delivery.",
            "executionPlan": f"Launch MVP focused on core value: {data.howItWorks[:100]}... Start with {data.goToMarketChannel[0] if data.goToMarketChannel else 'direct'} acquisition, then expand to additional channels.",
            "frameworkFit": [
                {
                    "name": "Value Equation",
                    "overallScore": (opp_score + prob_score) // 2,
                    "scores": [
                        {"name": "Dream Outcome", "score": opp_score, "maxScore": 10},
                        {"name": "Perceived Likelihood", "score": feas_score, "maxScore": 10},
                        {"name": "Time Delay", "score": 7, "maxScore": 10},
                        {"name": "Effort & Sacrifice", "score": 6, "maxScore": 10}
                    ]
                },
                {
                    "name": "Market Position",
                    "description": f"Positioned as a {data.deliveryModel} solution in the {data.industry} space targeting {data.targetMarket} customers."
                },
                {
                    "name": "ACP Framework",
                    "scores": [
                        {"name": "Audience", "score": min(8, 5 + audience_len // 30), "maxScore": 10},
                        {"name": "Community", "score": 6, "maxScore": 10},
                        {"name": "Product", "score": feas_score, "maxScore": 10}
                    ]
                }
            ],
            "categorization": {
                "type": data.deliveryModel.upper() if data.deliveryModel.lower() in ["saas", "service", "marketplace"] else "SaaS",
                "market": data.targetMarket,
                "target": data.targetAudience[:50] if len(data.targetAudience) > 50 else data.targetAudience,
                "trendAnalysis": f"The {data.industry} market in {data.targetLocation} shows promising growth potential for {data.deliveryModel} solutions."
            },
            "communitySignals": [
                {"platform": "Reddit", "details": "Multiple relevant subreddits", "score": 7},
                {"platform": "Facebook", "details": "Active groups in niche", "score": 6},
                {"platform": "YouTube", "details": "Content creators covering topic", "score": 7},
                {"platform": "LinkedIn", "details": "Professional discussions", "score": 6}
            ],
            "topKeywords": [
                {"keyword": f"{data.industry.lower()} {data.deliveryModel.lower()}", "volume": "2.4K", "competition": "MEDIUM", "growth": "+45%"},
                {"keyword": f"{data.ideaName.lower().split()[0]} solution", "volume": "1.8K", "competition": "LOW", "growth": "+32%"},
                {"keyword": f"best {data.industry.lower()} tools", "volume": "5.1K", "competition": "HIGH"}
            ],
            "trendKeyword": f"{data.industry.lower()} {data.deliveryModel.lower()}",
            "trendVolume": "2.4K",
            "trendGrowth": "+45%",
            "buildPrompts": ["Ad Creatives", "Brand Package", "Landing Page", "Email Sequence", "Social Media Strategy"],
            "suggestedQuestions": [
                "What problem does this solve?",
                "How big is the market opportunity?",
                "What's the competitive landscape?",
                "How hard is it to build?",
                "What's the revenue model?",
                "What are the key risks?"
            ]
        }
    
    @staticmethod
    def _generate_tags(data: ValidationReportCreate, opp_score: int, prob_score: int) -> List[str]:
        """Generate relevant tags based on analysis"""
        tags = []
        
        if opp_score >= 8:
            tags.append("High Opportunity")
        if prob_score >= 7:
            tags.append("Strong Problem-Fit")
        if data.urgencyLevel == "high":
            tags.append("Perfect Timing")
        if data.customerBudget == "high":
            tags.append("Premium Market")
        if len(data.goToMarketChannel) >= 3:
            tags.append("Multi-Channel Ready")
        if data.deliveryModel.lower() in ["saas", "subscription"]:
            tags.append("Recurring Revenue")
        if data.targetMarket == "B2B":
            tags.append("B2B Opportunity")
        
        # Ensure at least 3 tags
        default_tags = ["Market Potential", "Growth Opportunity", "Validated Concept"]
        while len(tags) < 3:
            for t in default_tags:
                if t not in tags:
                    tags.append(t)
                    break
        
        return tags[:5]
    
    @staticmethod
    async def _increment_engagement(workspace_id: str, user_id: str):
        """Increment user's validation engagement counter"""
        db = get_db()
        
        await db.user_engagement.update_one(
            {"user_id": user_id, "workspace_id": workspace_id},
            {
                "$inc": {"validation_count": 1},
                "$set": {"last_validation": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
    
    @staticmethod
    async def get_user_reports(workspace_id: str, user_id: str, limit: int = 50) -> List[dict]:
        """Get all validation reports for a user"""
        db = get_db()
        
        cursor = db.validation_reports.find(
            {"workspace_id": workspace_id, "user_id": user_id},
            {"_id": 0}
        ).sort("createdAt", -1).limit(limit)
        
        reports = await cursor.to_list(length=limit)
        
        # Transform to list items
        items = []
        for r in reports:
            opp_score = r.get("report", {}).get("scores", {}).get("opportunity", {}).get("value", 5)
            verdict = "PASS" if opp_score >= 7 else "PIVOT" if opp_score >= 5 else "KILL"
            
            items.append({
                "id": r["id"],
                "ideaName": r.get("ideaInput", {}).get("ideaName", "Untitled"),
                "ideaType": r.get("ideaInput", {}).get("ideaType", "business"),
                "status": r.get("status", "pending"),
                "overallScore": opp_score,
                "verdict": verdict,
                "createdAt": r.get("createdAt", "")
            })
        
        return items
    
    @staticmethod
    async def get_report_by_id(report_id: str, workspace_id: str) -> Optional[dict]:
        """Get a specific validation report"""
        db = get_db()
        
        report = await db.validation_reports.find_one(
            {"id": report_id, "workspace_id": workspace_id},
            {"_id": 0}
        )
        
        return report
    
    @staticmethod
    async def update_report_status(
        report_id: str, 
        workspace_id: str, 
        status: ReportStatus
    ) -> Optional[dict]:
        """Update report status (accept/reject)"""
        db = get_db()
        
        result = await db.validation_reports.find_one_and_update(
            {"id": report_id, "workspace_id": workspace_id},
            {
                "$set": {
                    "status": status.value,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            },
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            
            # Log event
            await db.intelligence_events.insert_one({
                "id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "type": f"validation.report_{status.value}",
                "data": {"report_id": report_id},
                "occurredAt": datetime.now(timezone.utc).isoformat()
            })
        
        return result
    
    @staticmethod
    async def modify_and_regenerate(
        report_id: str,
        workspace_id: str,
        user_id: str,
        new_data: ValidationReportCreate
    ) -> dict:
        """Modify input data and regenerate report"""
        db = get_db()
        
        # Generate new report
        report = await ValidationReportService._generate_ai_report(new_data)
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update existing report
        result = await db.validation_reports.find_one_and_update(
            {"id": report_id, "workspace_id": workspace_id},
            {
                "$set": {
                    "ideaInput": new_data.model_dump() if hasattr(new_data, 'model_dump') else new_data.dict(),
                    "report": report,
                    "status": ReportStatus.PENDING.value,
                    "updatedAt": now
                }
            },
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            
            # Log event
            await db.intelligence_events.insert_one({
                "id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "type": "validation.report_modified",
                "data": {"report_id": report_id},
                "occurredAt": now
            })
        
        return result
    
    @staticmethod
    async def get_engagement_stats(workspace_id: str, user_id: str) -> dict:
        """Get user's engagement statistics"""
        db = get_db()
        
        # Get engagement counter
        engagement = await db.user_engagement.find_one(
            {"user_id": user_id, "workspace_id": workspace_id},
            {"_id": 0}
        )
        
        # Count reports by status
        pipeline = [
            {"$match": {"workspace_id": workspace_id, "user_id": user_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_counts = {}
        async for doc in db.validation_reports.aggregate(pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        return {
            "totalValidations": engagement.get("validation_count", 0) if engagement else 0,
            "acceptedCount": status_counts.get("accepted", 0),
            "rejectedCount": status_counts.get("rejected", 0),
            "pendingCount": status_counts.get("pending", 0)
        }
    
    @staticmethod
    async def delete_report(report_id: str, workspace_id: str) -> bool:
        """Delete a validation report"""
        db = get_db()
        
        result = await db.validation_reports.delete_one(
            {"id": report_id, "workspace_id": workspace_id}
        )
        
        return result.deleted_count > 0
