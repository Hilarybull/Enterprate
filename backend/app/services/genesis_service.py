"""Genesis AI service for Business/Product Idea Validation"""
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
from app.core.database import get_db
from app.schemas.genesis import (
    ValidationIdeaRequest, 
    ValidationReport,
    ScoreBreakdown,
    OutputCard,
    IdeaScoreRequest
)

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class GenesisService:
    """Service for Genesis AI Business/Product Idea Validation"""
    
    # Scoring weights for Business Ideas
    BUSINESS_WEIGHTS = {
        "problem_validity": 15,
        "target_market": 15,
        "value_proposition": 15,
        "business_model": 15,
        "competition_differentiation": 15,
        "go_to_market_readiness": 10,
        "operational_feasibility": 10,
        "risk_sustainability": 5
    }
    
    # Scoring weights for Product Ideas
    PRODUCT_WEIGHTS = {
        "user_problem_fit": 15,
        "target_users": 10,
        "solution_effectiveness": 15,
        "product_differentiation": 15,
        "product_market_fit": 15,
        "build_feasibility": 15,
        "adoption_growth_risk": 10,
        "monetisation_potential": 5
    }
    
    @staticmethod
    async def validate_idea(workspace_id: str, user_id: str, data: ValidationIdeaRequest) -> dict:
        """Validate a business or product idea with AI scoring"""
        db = get_db()
        
        idea_type = data.ideaType.lower()
        
        # Generate scores based on idea type
        if idea_type == "business":
            report = await GenesisService._score_business_idea(data)
        else:
            report = await GenesisService._score_product_idea(data)
        
        # Create result document
        result_id = str(uuid.uuid4())
        result = {
            "id": result_id,
            "workspace_id": workspace_id,
            "ideaType": data.ideaType,
            "ideaName": data.ideaName,
            "ideaDescription": data.ideaDescription,
            "industry": data.industry,
            "subIndustry": data.subIndustry,
            "problemSolved": data.problemSolved,
            "targetAudience": data.targetAudience,
            "urgencyLevel": data.urgencyLevel,
            "howItWorks": data.howItWorks,
            "deliveryModel": data.deliveryModel,
            "targetMarket": data.targetMarket,
            "targetLocation": data.targetLocation,
            "customerBudget": data.customerBudget,
            "goToMarketChannel": data.goToMarketChannel,
            "report": report,
            "created_by": user_id,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in database
        await db.genesis_validations.insert_one(result)
        
        # Log intelligence event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": f"genesis.{idea_type}_validated",
            "data": {
                "idea_name": data.ideaName,
                "score": report["overallScore"],
                "verdict": report["verdict"]
            },
            "occurredAt": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "id": result_id,
            "ideaType": data.ideaType,
            "ideaName": data.ideaName,
            "report": report,
            "createdAt": result["createdAt"]
        }
    
    @staticmethod
    async def _score_business_idea(data: ValidationIdeaRequest) -> dict:
        """Score a business idea using the defined weights"""
        scores = []
        total_score = 0
        
        # 1. Problem Validity (15 pts)
        problem_score = GenesisService._assess_problem_validity(data)
        scores.append(ScoreBreakdown(
            name="Problem Validity",
            score=problem_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(problem_score, 15)
        ).model_dump())
        total_score += problem_score
        
        # 2. Target Market (15 pts)
        market_score = GenesisService._assess_target_market(data)
        scores.append(ScoreBreakdown(
            name="Target Market",
            score=market_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(market_score, 15)
        ).model_dump())
        total_score += market_score
        
        # 3. Value Proposition (15 pts)
        value_score = GenesisService._assess_value_proposition(data)
        scores.append(ScoreBreakdown(
            name="Value Proposition",
            score=value_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(value_score, 15)
        ).model_dump())
        total_score += value_score
        
        # 4. Business Model (15 pts)
        model_score = GenesisService._assess_business_model(data)
        scores.append(ScoreBreakdown(
            name="Business Model",
            score=model_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(model_score, 15)
        ).model_dump())
        total_score += model_score
        
        # 5. Competition & Differentiation (15 pts)
        comp_score = GenesisService._assess_competition(data)
        scores.append(ScoreBreakdown(
            name="Competition & Differentiation",
            score=comp_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(comp_score, 15)
        ).model_dump())
        total_score += comp_score
        
        # 6. Go-To-Market Readiness (10 pts)
        gtm_score = GenesisService._assess_gtm_readiness(data)
        scores.append(ScoreBreakdown(
            name="Go-To-Market Readiness",
            score=gtm_score,
            maxScore=10,
            assessment=GenesisService._get_assessment(gtm_score, 10)
        ).model_dump())
        total_score += gtm_score
        
        # 7. Operational Feasibility (10 pts)
        ops_score = GenesisService._assess_operational_feasibility(data)
        scores.append(ScoreBreakdown(
            name="Operational Feasibility",
            score=ops_score,
            maxScore=10,
            assessment=GenesisService._get_assessment(ops_score, 10)
        ).model_dump())
        total_score += ops_score
        
        # 8. Risk & Sustainability (5 pts)
        risk_score = GenesisService._assess_risk_sustainability(data)
        scores.append(ScoreBreakdown(
            name="Risk & Sustainability",
            score=risk_score,
            maxScore=5,
            assessment=GenesisService._get_assessment(risk_score, 5)
        ).model_dump())
        total_score += risk_score
        
        # Determine verdict
        verdict, verdict_reason = GenesisService._get_business_verdict(total_score, data)
        
        # Generate output cards for business
        output_cards = GenesisService._generate_business_output_cards(total_score, scores, data)
        
        # Generate insights
        strengths = GenesisService._identify_strengths(scores)
        weak_areas = GenesisService._identify_weak_areas(scores)
        key_risks = GenesisService._identify_business_risks(data, scores)
        recommendations = GenesisService._generate_business_recommendations(data, scores, verdict)
        next_experiments = GenesisService._generate_next_experiments(data, "business")
        
        return {
            "overallScore": total_score,
            "verdict": verdict,
            "verdictReason": verdict_reason,
            "scoreBreakdown": scores,
            "outputCards": output_cards,
            "strengths": strengths,
            "weakAreas": weak_areas,
            "keyRisks": key_risks,
            "recommendations": recommendations,
            "marketAssessment": GenesisService._get_market_assessment(data),
            "competitiveLandscape": GenesisService._get_competitive_landscape(data),
            "feasibilityNotes": GenesisService._get_feasibility_notes(data),
            "nextExperiments": next_experiments
        }
    
    @staticmethod
    async def _score_product_idea(data: ValidationIdeaRequest) -> dict:
        """Score a product idea using the defined weights"""
        scores = []
        total_score = 0
        
        # 1. User Problem Fit (15 pts)
        problem_score = GenesisService._assess_user_problem_fit(data)
        scores.append(ScoreBreakdown(
            name="User Problem Fit",
            score=problem_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(problem_score, 15)
        ).model_dump())
        total_score += problem_score
        
        # 2. Target Users (10 pts)
        users_score = GenesisService._assess_target_users(data)
        scores.append(ScoreBreakdown(
            name="Target Users",
            score=users_score,
            maxScore=10,
            assessment=GenesisService._get_assessment(users_score, 10)
        ).model_dump())
        total_score += users_score
        
        # 3. Solution Effectiveness (15 pts)
        solution_score = GenesisService._assess_solution_effectiveness(data)
        scores.append(ScoreBreakdown(
            name="Solution Effectiveness",
            score=solution_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(solution_score, 15)
        ).model_dump())
        total_score += solution_score
        
        # 4. Product Differentiation (15 pts)
        diff_score = GenesisService._assess_product_differentiation(data)
        scores.append(ScoreBreakdown(
            name="Product Differentiation",
            score=diff_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(diff_score, 15)
        ).model_dump())
        total_score += diff_score
        
        # 5. Product-Market Fit Signals (15 pts)
        pmf_score = GenesisService._assess_pmf_signals(data)
        scores.append(ScoreBreakdown(
            name="Product-Market Fit Signals",
            score=pmf_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(pmf_score, 15)
        ).model_dump())
        total_score += pmf_score
        
        # 6. Build & Technical Feasibility (15 pts)
        build_score = GenesisService._assess_build_feasibility(data)
        scores.append(ScoreBreakdown(
            name="Build & Technical Feasibility",
            score=build_score,
            maxScore=15,
            assessment=GenesisService._get_assessment(build_score, 15)
        ).model_dump())
        total_score += build_score
        
        # 7. Adoption & Growth Risk (10 pts)
        adoption_score = GenesisService._assess_adoption_risk(data)
        scores.append(ScoreBreakdown(
            name="Adoption & Growth Risk",
            score=adoption_score,
            maxScore=10,
            assessment=GenesisService._get_assessment(adoption_score, 10)
        ).model_dump())
        total_score += adoption_score
        
        # 8. Monetisation Potential (5 pts)
        monetise_score = GenesisService._assess_monetisation(data)
        scores.append(ScoreBreakdown(
            name="Monetisation Potential",
            score=monetise_score,
            maxScore=5,
            assessment=GenesisService._get_assessment(monetise_score, 5)
        ).model_dump())
        total_score += monetise_score
        
        # Determine verdict
        verdict, verdict_reason = GenesisService._get_product_verdict(total_score, data)
        
        # Generate output cards for product
        output_cards = GenesisService._generate_product_output_cards(total_score, scores, data)
        
        # Generate insights
        strengths = GenesisService._identify_strengths(scores)
        weak_areas = GenesisService._identify_weak_areas(scores)
        key_risks = GenesisService._identify_product_risks(data, scores)
        recommendations = GenesisService._generate_product_recommendations(data, scores, verdict)
        next_experiments = GenesisService._generate_next_experiments(data, "product")
        
        return {
            "overallScore": total_score,
            "verdict": verdict,
            "verdictReason": verdict_reason,
            "scoreBreakdown": scores,
            "outputCards": output_cards,
            "strengths": strengths,
            "weakAreas": weak_areas,
            "keyRisks": key_risks,
            "recommendations": recommendations,
            "feasibilityNotes": GenesisService._get_product_feasibility_notes(data),
            "nextExperiments": next_experiments
        }
    
    # === SCORING HELPER METHODS ===
    
    @staticmethod
    def _get_assessment(score: int, max_score: int) -> str:
        ratio = score / max_score
        if ratio >= 0.8:
            return "Strong"
        elif ratio >= 0.6:
            return "Moderate"
        elif ratio >= 0.4:
            return "Weak"
        else:
            return "Critical"
    
    @staticmethod
    def _assess_problem_validity(data: ValidationIdeaRequest) -> int:
        score = 0
        # Check problem description quality
        if len(data.problemSolved) > 100:
            score += 5
        elif len(data.problemSolved) > 50:
            score += 3
        else:
            score += 1
        
        # Check urgency level
        if data.urgencyLevel == "high":
            score += 5
        elif data.urgencyLevel == "medium":
            score += 3
        else:
            score += 1
        
        # Check target audience clarity
        if len(data.targetAudience) > 30:
            score += 5
        elif len(data.targetAudience) > 15:
            score += 3
        else:
            score += 1
        
        return min(score, 15)
    
    @staticmethod
    def _assess_target_market(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Market type clarity
        if data.targetMarket in ["B2B", "B2C", "B2G"]:
            score += 5
        else:
            score += 2
        
        # Location specificity
        if len(data.targetLocation) > 10:
            score += 5
        else:
            score += 2
        
        # Customer budget insight
        if data.customerBudget in ["medium", "high"]:
            score += 5
        elif data.customerBudget == "low":
            score += 3
        else:
            score += 1
        
        return min(score, 15)
    
    @staticmethod
    def _assess_value_proposition(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Idea description quality
        if len(data.ideaDescription) > 200:
            score += 7
        elif len(data.ideaDescription) > 100:
            score += 5
        else:
            score += 2
        
        # How it works clarity
        if len(data.howItWorks) > 150:
            score += 8
        elif len(data.howItWorks) > 75:
            score += 5
        else:
            score += 2
        
        return min(score, 15)
    
    @staticmethod
    def _assess_business_model(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Delivery model clarity
        strong_models = ["subscription", "saas", "marketplace"]
        moderate_models = ["service", "agency"]
        
        if data.deliveryModel.lower() in strong_models:
            score += 10
        elif data.deliveryModel.lower() in moderate_models:
            score += 7
        else:
            score += 4
        
        # Customer budget alignment
        if data.customerBudget != "unknown":
            score += 5
        else:
            score += 2
        
        return min(score, 15)
    
    @staticmethod
    def _assess_competition(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Industry has known competition level
        competitive_industries = ["technology", "retail", "food", "finance"]
        moderate_industries = ["health", "education", "real estate"]
        
        if data.industry.lower() in competitive_industries:
            score += 7  # Harder but validated market
        elif data.industry.lower() in moderate_industries:
            score += 10
        else:
            score += 12
        
        # Differentiation potential from description
        if len(data.howItWorks) > 100:
            score += 3
        
        return min(score, 15)
    
    @staticmethod
    def _assess_gtm_readiness(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Number of go-to-market channels
        num_channels = len(data.goToMarketChannel)
        if num_channels >= 3:
            score += 6
        elif num_channels >= 2:
            score += 4
        else:
            score += 2
        
        # Quality of channels
        strong_channels = ["seo", "partnerships", "direct sales"]
        for channel in data.goToMarketChannel:
            if channel.lower() in strong_channels:
                score += 2
                break
        
        # Target location clarity
        if data.targetLocation and len(data.targetLocation) > 5:
            score += 2
        
        return min(score, 10)
    
    @staticmethod
    def _assess_operational_feasibility(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Delivery model complexity
        simple_models = ["digital", "saas", "mobile app"]
        moderate_models = ["service", "subscription"]
        
        if data.deliveryModel.lower() in simple_models:
            score += 7
        elif data.deliveryModel.lower() in moderate_models:
            score += 5
        else:
            score += 3
        
        # Location scope
        if "global" in data.targetLocation.lower():
            score += 2  # Ambitious but risky
        else:
            score += 3  # Focused is better
        
        return min(score, 10)
    
    @staticmethod
    def _assess_risk_sustainability(data: ValidationIdeaRequest) -> int:
        score = 2  # Base score
        
        # Recurring revenue models score higher
        if data.deliveryModel.lower() in ["subscription", "saas"]:
            score += 2
        
        # Multiple channels reduce risk
        if len(data.goToMarketChannel) >= 2:
            score += 1
        
        return min(score, 5)
    
    # === PRODUCT SCORING METHODS ===
    
    @staticmethod
    def _assess_user_problem_fit(data: ValidationIdeaRequest) -> int:
        return GenesisService._assess_problem_validity(data)
    
    @staticmethod
    def _assess_target_users(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Audience clarity
        if len(data.targetAudience) > 50:
            score += 5
        elif len(data.targetAudience) > 25:
            score += 3
        else:
            score += 1
        
        # Market type
        if data.targetMarket in ["B2C", "B2B"]:
            score += 5
        else:
            score += 2
        
        return min(score, 10)
    
    @staticmethod
    def _assess_solution_effectiveness(data: ValidationIdeaRequest) -> int:
        return GenesisService._assess_value_proposition(data)
    
    @staticmethod
    def _assess_product_differentiation(data: ValidationIdeaRequest) -> int:
        return GenesisService._assess_competition(data)
    
    @staticmethod
    def _assess_pmf_signals(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Urgency indicates PMF potential
        if data.urgencyLevel == "high":
            score += 7
        elif data.urgencyLevel == "medium":
            score += 5
        else:
            score += 2
        
        # Customer budget indicates willingness to pay
        if data.customerBudget in ["medium", "high"]:
            score += 5
        elif data.customerBudget == "low":
            score += 3
        else:
            score += 1
        
        # Clear target market
        if data.targetMarket != "Other":
            score += 3
        
        return min(score, 15)
    
    @staticmethod
    def _assess_build_feasibility(data: ValidationIdeaRequest) -> int:
        score = 0
        
        # Delivery model complexity
        easy_build = ["digital", "mobile app"]
        moderate_build = ["saas", "physical"]
        
        if data.deliveryModel.lower() in easy_build:
            score += 10
        elif data.deliveryModel.lower() in moderate_build:
            score += 7
        else:
            score += 4
        
        # Scope from description
        if len(data.howItWorks) < 200:
            score += 5  # Simpler is often more feasible
        else:
            score += 3
        
        return min(score, 15)
    
    @staticmethod
    def _assess_adoption_risk(data: ValidationIdeaRequest) -> int:
        score = 5  # Base score
        
        # Multiple channels reduce adoption risk
        if len(data.goToMarketChannel) >= 3:
            score += 3
        elif len(data.goToMarketChannel) >= 2:
            score += 2
        
        # Known market type
        if data.targetMarket != "Other":
            score += 2
        
        return min(score, 10)
    
    @staticmethod
    def _assess_monetisation(data: ValidationIdeaRequest) -> int:
        score = 1  # Base score
        
        # Customer budget
        if data.customerBudget == "high":
            score += 3
        elif data.customerBudget == "medium":
            score += 2
        elif data.customerBudget == "low":
            score += 1
        
        # Recurring model
        if data.deliveryModel.lower() in ["subscription", "saas"]:
            score += 1
        
        return min(score, 5)
    
    # === VERDICT LOGIC ===
    
    @staticmethod
    def _get_business_verdict(score: int, data: ValidationIdeaRequest) -> tuple:
        # Check auto-kill triggers
        if len(data.problemSolved) < 30:
            return ("KILL", "Weak or unclear problem statement")
        if data.targetMarket == "Other" and len(data.targetAudience) < 20:
            return ("KILL", "No identifiable target market")
        if data.deliveryModel.lower() == "other" and data.customerBudget == "unknown":
            return ("KILL", "No clear revenue model")
        
        # Score-based verdict
        if score >= 75:
            return ("PASS", "Strong validation signals. Proceed to build & launch.")
        elif score >= 50:
            return ("PIVOT", "Moderate potential. Refine market, pricing, or model before proceeding.")
        else:
            return ("KILL", "High risk. Consider significant changes or alternative ideas.")
    
    @staticmethod
    def _get_product_verdict(score: int, data: ValidationIdeaRequest) -> tuple:
        # Check auto-kill triggers
        if len(data.problemSolved) < 30:
            return ("KILL", "No strong user pain identified")
        if data.urgencyLevel == "low" and data.customerBudget == "unknown":
            return ("KILL", "Low adoption likelihood")
        if data.deliveryModel.lower() == "other":
            return ("KILL", "MVP not feasible within constraints")
        
        # Score-based verdict
        if score >= 75:
            return ("PASS", "Strong product signals. Build MVP and test with users.")
        elif score >= 50:
            return ("PIVOT", "Improve product-market fit or differentiation before building.")
        else:
            return ("KILL", "High adoption or feasibility risk. Reconsider approach.")
    
    # === OUTPUT CARD GENERATORS ===
    
    @staticmethod
    def _generate_business_output_cards(score: int, breakdown: list, data: ValidationIdeaRequest) -> list:
        cards = []
        
        # 1. Overall Business Viability Score
        cards.append({
            "title": "Overall Business Viability Score",
            "value": f"{score}/100",
            "status": "positive" if score >= 75 else "neutral" if score >= 50 else "negative"
        })
        
        # 2. Problem Strength
        problem_score = next((s for s in breakdown if s["name"] == "Problem Validity"), None)
        problem_strength = problem_score["assessment"] if problem_score else "Unknown"
        cards.append({
            "title": "Problem Strength",
            "value": problem_strength,
            "status": "positive" if problem_strength == "Strong" else "neutral" if problem_strength == "Moderate" else "negative"
        })
        
        # 3. Market Attractiveness
        market_score = next((s for s in breakdown if s["name"] == "Target Market"), None)
        cards.append({
            "title": "Market Attractiveness",
            "value": market_score["assessment"] if market_score else "Unknown",
            "description": f"{data.targetMarket} in {data.targetLocation}"
        })
        
        # 4. Revenue Sustainability
        model_score = next((s for s in breakdown if s["name"] == "Business Model"), None)
        cards.append({
            "title": "Revenue Sustainability",
            "value": model_score["assessment"] if model_score else "Unknown",
            "description": f"{data.deliveryModel} model"
        })
        
        # 5. Competitive Position
        comp_score = next((s for s in breakdown if s["name"] == "Competition & Differentiation"), None)
        intensity = "High" if comp_score and comp_score["score"] < 8 else "Medium" if comp_score and comp_score["score"] < 12 else "Low"
        cards.append({
            "title": "Competition Intensity",
            "value": intensity,
            "status": "negative" if intensity == "High" else "neutral"
        })
        
        # 6. Execution Difficulty
        ops_score = next((s for s in breakdown if s["name"] == "Operational Feasibility"), None)
        difficulty = "Low" if ops_score and ops_score["score"] >= 7 else "Medium" if ops_score and ops_score["score"] >= 4 else "High"
        cards.append({
            "title": "Execution Difficulty",
            "value": difficulty,
            "status": "positive" if difficulty == "Low" else "neutral" if difficulty == "Medium" else "negative"
        })
        
        return cards
    
    @staticmethod
    def _generate_product_output_cards(score: int, breakdown: list, data: ValidationIdeaRequest) -> list:
        cards = []
        
        # 1. Product Validation Score
        cards.append({
            "title": "Product Validation Score",
            "value": f"{score}/100",
            "status": "positive" if score >= 75 else "neutral" if score >= 50 else "negative"
        })
        
        # 2. User Pain Strength
        problem_score = next((s for s in breakdown if s["name"] == "User Problem Fit"), None)
        cards.append({
            "title": "User Pain Strength",
            "value": problem_score["assessment"] if problem_score else "Unknown",
            "status": "positive" if problem_score and problem_score["assessment"] == "Strong" else "neutral"
        })
        
        # 3. Adoption Readiness
        adoption_score = next((s for s in breakdown if s["name"] == "Adoption & Growth Risk"), None)
        readiness = "High" if adoption_score and adoption_score["score"] >= 7 else "Medium" if adoption_score and adoption_score["score"] >= 4 else "Low"
        cards.append({
            "title": "Adoption Readiness",
            "value": readiness,
            "status": "positive" if readiness == "High" else "neutral"
        })
        
        # 4. Differentiation Strength
        diff_score = next((s for s in breakdown if s["name"] == "Product Differentiation"), None)
        cards.append({
            "title": "Differentiation Strength",
            "value": diff_score["assessment"] if diff_score else "Unknown"
        })
        
        # 5. MVP Feasibility
        build_score = next((s for s in breakdown if s["name"] == "Build & Technical Feasibility"), None)
        feasibility = "High" if build_score and build_score["score"] >= 10 else "Medium" if build_score and build_score["score"] >= 6 else "Low"
        cards.append({
            "title": "MVP Feasibility",
            "value": feasibility,
            "status": "positive" if feasibility == "High" else "neutral" if feasibility == "Medium" else "negative"
        })
        
        # 6. Time-to-Market
        time_estimate = "Fast" if data.deliveryModel.lower() in ["digital", "mobile app"] else "Medium" if data.deliveryModel.lower() in ["saas"] else "Slow"
        cards.append({
            "title": "Time-to-Market",
            "value": time_estimate,
            "description": f"{data.deliveryModel} delivery"
        })
        
        return cards
    
    # === INSIGHT GENERATORS ===
    
    @staticmethod
    def _identify_strengths(scores: list) -> list:
        strengths = []
        for score in scores:
            if score["assessment"] == "Strong":
                strengths.append(f"{score['name']}: {score['score']}/{score['maxScore']} - Strong foundation")
        return strengths if strengths else ["No outstanding strengths identified - consider improvements across all areas"]
    
    @staticmethod
    def _identify_weak_areas(scores: list) -> list:
        weak = []
        for score in scores:
            if score["assessment"] in ["Weak", "Critical"]:
                weak.append(f"{score['name']}: {score['score']}/{score['maxScore']} - Needs improvement")
        return weak if weak else ["No critical weaknesses identified"]
    
    @staticmethod
    def _identify_business_risks(data: ValidationIdeaRequest, scores: list) -> list:
        risks = []
        
        if data.customerBudget == "unknown":
            risks.append("Unclear customer willingness to pay")
        if data.targetMarket == "Other":
            risks.append("Undefined target market segment")
        if len(data.goToMarketChannel) < 2:
            risks.append("Limited go-to-market channels")
        if data.urgencyLevel == "low":
            risks.append("Low urgency may affect conversion rates")
        
        return risks if risks else ["Standard market risks apply"]
    
    @staticmethod
    def _identify_product_risks(data: ValidationIdeaRequest, scores: list) -> list:
        risks = []
        
        if data.urgencyLevel == "low":
            risks.append("Low user pain urgency may slow adoption")
        if data.deliveryModel.lower() == "physical":
            risks.append("Physical products have higher operational complexity")
        if len(data.targetAudience) < 30:
            risks.append("Target user definition needs more clarity")
        
        return risks if risks else ["Standard product development risks apply"]
    
    @staticmethod
    def _generate_business_recommendations(data, scores, verdict) -> list:
        recs = []
        
        if verdict == "PASS":
            recs.append("Develop detailed business plan with financial projections")
            recs.append("Start customer discovery interviews")
            recs.append("Build minimum viable offering")
        elif verdict == "PIVOT":
            recs.append("Conduct deeper market research to validate demand")
            recs.append("Refine value proposition based on customer feedback")
            recs.append("Test pricing with target audience")
        else:
            recs.append("Revisit problem definition with potential customers")
            recs.append("Explore adjacent market opportunities")
            recs.append("Consider alternative business models")
        
        return recs
    
    @staticmethod
    def _generate_product_recommendations(data, scores, verdict) -> list:
        recs = []
        
        if verdict == "PASS":
            recs.append("Build MVP with core features only")
            recs.append("Recruit early adopter beta testers")
            recs.append("Set up analytics to track key metrics")
        elif verdict == "PIVOT":
            recs.append("Conduct user interviews to validate pain points")
            recs.append("Create clickable prototype for user testing")
            recs.append("Identify unique differentiators vs competitors")
        else:
            recs.append("Re-evaluate user problem and solution fit")
            recs.append("Consider simpler product approach")
            recs.append("Research successful products in adjacent space")
        
        return recs
    
    @staticmethod
    def _generate_next_experiments(data: ValidationIdeaRequest, idea_type: str) -> list:
        experiments = [
            "Run 5-10 customer discovery interviews",
            "Create landing page to measure interest",
            "Survey target audience about willingness to pay"
        ]
        
        if idea_type == "product":
            experiments.append("Build clickable prototype and gather feedback")
            experiments.append("Test core feature with small user group")
        else:
            experiments.append("Validate pricing with 3 potential customers")
            experiments.append("Map competitive landscape in detail")
        
        return experiments[:5]
    
    @staticmethod
    def _get_market_assessment(data: ValidationIdeaRequest) -> str:
        return f"{data.targetMarket} market in {data.targetLocation} with {data.customerBudget} budget customers. Primary channels: {', '.join(data.goToMarketChannel[:3])}"
    
    @staticmethod
    def _get_competitive_landscape(data: ValidationIdeaRequest) -> str:
        return f"{data.industry} industry typically has moderate to high competition. Focus on differentiation through {data.deliveryModel} delivery model."
    
    @staticmethod
    def _get_feasibility_notes(data: ValidationIdeaRequest) -> str:
        return f"Operating with {data.deliveryModel} model. Key focus areas: customer acquisition through {', '.join(data.goToMarketChannel[:2])}."
    
    @staticmethod
    def _get_product_feasibility_notes(data: ValidationIdeaRequest) -> str:
        return f"{data.deliveryModel} product targeting {data.targetAudience}. Build complexity appears {'manageable' if data.deliveryModel.lower() in ['digital', 'saas', 'mobile app'] else 'significant'}."
    
    # === LEGACY SUPPORT ===
    
    @staticmethod
    async def score_idea(workspace_id: str, user_id: str, data: IdeaScoreRequest) -> dict:
        """Legacy idea scoring - simple version"""
        db = get_db()
        import random
        
        analysis = {
            "marketSize": random.randint(60, 95),
            "competition": random.randint(50, 90),
            "feasibility": random.randint(55, 95),
            "scalability": random.randint(60, 90),
            "revenue": random.randint(50, 85)
        }
        
        overall_score = sum(analysis.values()) // len(analysis)
        
        result = {
            "id": str(uuid.uuid4()),
            "score": overall_score,
            "analysis": analysis,
            "insights": [
                "Your idea shows market potential",
                "Consider customer validation next",
                "Competitive landscape requires differentiation"
            ],
            "nextSteps": [
                "Conduct customer interviews",
                "Build MVP prototype",
                "Test pricing assumptions"
            ]
        }
        
        return result
