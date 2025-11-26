"""Genesis AI service for idea validation"""
import uuid
import random
from datetime import datetime, timezone
from app.core.database import get_db
from app.schemas.genesis import IdeaScoreRequest

class GenesisService:
    """Service for Genesis AI operations"""
    
    @staticmethod
    async def score_idea(workspace_id: str, user_id: str, data: IdeaScoreRequest) -> dict:
        """Score a business idea using AI analysis"""
        db = get_db()
        
        # Generate scores (in production, use actual AI)
        analysis = {
            "marketSize": random.randint(60, 95),
            "competition": random.randint(50, 90),
            "feasibility": random.randint(55, 95),
            "scalability": random.randint(60, 90),
            "revenue": random.randint(50, 85)
        }
        
        overall_score = sum(analysis.values()) // len(analysis)
        
        insights = [
            f"Your idea targets a market with strong growth potential.",
            f"Consider focusing on {data.targetCustomer or 'your target audience'} for initial traction.",
            "The competitive landscape shows room for differentiation.",
            "Revenue model viability looks promising with proper execution."
        ]
        
        next_steps = [
            "Conduct customer interviews to validate problem-solution fit",
            "Build a minimum viable product (MVP) to test core assumptions",
            "Create a go-to-market strategy focusing on early adopters",
            "Develop financial projections for the first 12 months"
        ]
        
        result = {
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "idea": data.idea,
            "target_customer": data.targetCustomer,
            "score": overall_score,
            "analysis": analysis,
            "insights": insights,
            "nextSteps": next_steps,
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store result
        await db.genesis_results.insert_one(result)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "genesis.idea_scored",
            "data": {"score": overall_score, "idea_preview": data.idea[:100]},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        })
        
        return {k: v for k, v in result.items() if k != '_id'}
