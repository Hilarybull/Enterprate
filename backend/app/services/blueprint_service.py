"""Business Blueprint service with AI generation"""
import uuid
import os
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.blueprint import (
    BlueprintCreate, BlueprintUpdate, BlueprintSectionType,
    SWOTAnalysis, FinancialProjection
)

# Try to import LLM integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class BlueprintService:
    """Service for Business Blueprint generation"""
    
    SECTION_PROMPTS = {
        "executive_summary": """Generate a professional executive summary for a business plan.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Target Market: {target_market}
            Business Model: {business_model}
            
            Include: mission statement, value proposition, key success factors, and funding requirements.
            Keep it concise (300-400 words) and compelling for investors.""",
        
        "market_analysis": """Generate a comprehensive market analysis section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Target Market: {target_market}
            
            Include: market size, growth trends, target customer segments, and market dynamics.
            Provide specific insights relevant to the industry.""",
        
        "products_services": """Generate a products and services section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Business Model: {business_model}
            
            Include: core offerings, features and benefits, pricing strategy, and competitive advantages.""",
        
        "marketing_strategy": """Generate a marketing strategy section.
            Business: {business_name}
            Industry: {industry}
            Target Market: {target_market}
            Business Model: {business_model}
            
            Include: positioning, marketing channels, customer acquisition strategy, and brand messaging.""",
        
        "operations_plan": """Generate an operations plan section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Business Model: {business_model}
            
            Include: operational workflow, key processes, resource requirements, and technology needs.""",
        
        "financial_projections": """Generate a financial projections narrative.
            Business: {business_name}
            Industry: {industry}
            Business Model: {business_model}
            Funding Goal: {funding_goal}
            
            Include: revenue model, cost structure, break-even analysis, and 3-year projection summary.""",
        
        "competitive_analysis": """Generate a competitive analysis section.
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Target Market: {target_market}
            
            Include: key competitors, competitive landscape, differentiation strategy, and market positioning."""
    }
    
    @staticmethod
    async def create_blueprint(workspace_id: str, user_id: str, data: BlueprintCreate) -> dict:
        """Create a new business blueprint"""
        db = get_db()
        
        blueprint_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        blueprint = {
            "id": blueprint_id,
            "workspace_id": workspace_id,
            "businessName": data.businessName,
            "industry": data.industry,
            "description": data.description,
            "targetMarket": data.targetMarket,
            "businessModel": data.businessModel,
            "fundingGoal": data.fundingGoal,
            "status": "draft",
            "sections": [],
            "swotAnalysis": None,
            "financialProjections": [],
            "created_by": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.blueprints.insert_one(blueprint)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "blueprint.created",
            "data": {"blueprint_id": blueprint_id, "business_name": data.businessName},
            "occurredAt": now
        })
        
        return {k: v for k, v in blueprint.items() if k != '_id'}
    
    @staticmethod
    async def get_blueprints(workspace_id: str) -> List[dict]:
        """Get all blueprints for a workspace"""
        db = get_db()
        
        blueprints = await db.blueprints.find(
            {"workspace_id": workspace_id}
        ).sort("createdAt", -1).to_list(length=100)
        
        return [{k: v for k, v in bp.items() if k != '_id'} for bp in blueprints]
    
    @staticmethod
    async def get_blueprint(blueprint_id: str, workspace_id: str) -> dict:
        """Get a specific blueprint"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        return {k: v for k, v in blueprint.items() if k != '_id'}
    
    @staticmethod
    async def generate_section(workspace_id: str, blueprint_id: str, section_type: str) -> dict:
        """Generate a specific section using AI"""
        db = get_db()
        
        # Get blueprint
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Generate content
        content = await BlueprintService._generate_with_ai(
            section_type,
            blueprint
        )
        
        # Create section
        section = {
            "sectionType": section_type,
            "title": BlueprintService._get_section_title(section_type),
            "content": content,
            "generatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        # Update blueprint
        existing_sections = blueprint.get("sections", [])
        # Remove existing section of same type
        existing_sections = [s for s in existing_sections if s.get("sectionType") != section_type]
        existing_sections.append(section)
        
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {
                "$set": {
                    "sections": existing_sections,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return section
    
    @staticmethod
    async def generate_swot(workspace_id: str, blueprint_id: str) -> dict:
        """Generate SWOT analysis using AI"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Generate SWOT with AI
        swot = await BlueprintService._generate_swot_with_ai(blueprint)
        
        # Update blueprint
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {
                "$set": {
                    "swotAnalysis": swot,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return swot
    
    @staticmethod
    async def generate_financials(workspace_id: str, blueprint_id: str) -> List[dict]:
        """Generate financial projections"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Generate projections (simplified model)
        projections = BlueprintService._generate_financial_projections(
            blueprint.get("fundingGoal", 100000),
            blueprint.get("businessModel", "subscription")
        )
        
        # Update blueprint
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {
                "$set": {
                    "financialProjections": projections,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return projections
    
    @staticmethod
    async def generate_full_blueprint(workspace_id: str, blueprint_id: str) -> dict:
        """Generate all sections at once"""
        sections_to_generate = [
            "executive_summary",
            "market_analysis",
            "products_services",
            "marketing_strategy",
            "operations_plan",
            "financial_projections",
            "competitive_analysis"
        ]
        
        for section_type in sections_to_generate:
            await BlueprintService.generate_section(workspace_id, blueprint_id, section_type)
        
        # Generate SWOT
        await BlueprintService.generate_swot(workspace_id, blueprint_id)
        
        # Generate financials
        await BlueprintService.generate_financials(workspace_id, blueprint_id)
        
        # Update status
        db = get_db()
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {"$set": {"status": "complete", "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        return await BlueprintService.get_blueprint(blueprint_id, workspace_id)
    
    @staticmethod
    async def update_blueprint(blueprint_id: str, workspace_id: str, data: BlueprintUpdate) -> dict:
        """Update a blueprint"""
        db = get_db()
        
        blueprint = await db.blueprints.find_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        if not blueprint:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        await db.blueprints.update_one(
            {"id": blueprint_id},
            {"$set": update_data}
        )
        
        return await BlueprintService.get_blueprint(blueprint_id, workspace_id)
    
    @staticmethod
    async def delete_blueprint(blueprint_id: str, workspace_id: str) -> bool:
        """Delete a blueprint"""
        db = get_db()
        
        result = await db.blueprints.delete_one({
            "id": blueprint_id,
            "workspace_id": workspace_id
        })
        
        return result.deleted_count > 0
    
    # Helper methods
    @staticmethod
    def _get_section_title(section_type: str) -> str:
        titles = {
            "executive_summary": "Executive Summary",
            "market_analysis": "Market Analysis",
            "products_services": "Products & Services",
            "marketing_strategy": "Marketing Strategy",
            "operations_plan": "Operations Plan",
            "financial_projections": "Financial Projections",
            "competitive_analysis": "Competitive Analysis",
            "swot_analysis": "SWOT Analysis"
        }
        return titles.get(section_type, section_type.replace("_", " ").title())
    
    @staticmethod
    async def _generate_with_ai(section_type: str, blueprint: dict) -> str:
        """Generate section content with AI"""
        if not LLM_AVAILABLE:
            return BlueprintService._get_fallback_content(section_type, blueprint)
        
        try:
            prompt_template = BlueprintService.SECTION_PROMPTS.get(section_type, "")
            prompt = prompt_template.format(
                business_name=blueprint.get("businessName", "the business"),
                industry=blueprint.get("industry", "general"),
                description=blueprint.get("description", "a new business"),
                target_market=blueprint.get("targetMarket", "general market"),
                business_model=blueprint.get("businessModel", "traditional"),
                funding_goal=blueprint.get("fundingGoal", 100000)
            )
            
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return BlueprintService._get_fallback_content(section_type, blueprint)
            
            chat = LlmChat(
                api_key=llm_key,
                model="gpt-4o",
                system_message="You are a professional business consultant creating business plan sections. Write clear, professional, and actionable content."
            )
            
            response = await chat.send_async(message=UserMessage(text=prompt))
            return response.text
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return BlueprintService._get_fallback_content(section_type, blueprint)
    
    @staticmethod
    async def _generate_swot_with_ai(blueprint: dict) -> dict:
        """Generate SWOT analysis with AI"""
        if not LLM_AVAILABLE:
            return BlueprintService._get_fallback_swot(blueprint)
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return BlueprintService._get_fallback_swot(blueprint)
            
            prompt = f"""Generate a SWOT analysis for this business:
            Business: {blueprint.get('businessName')}
            Industry: {blueprint.get('industry')}
            Description: {blueprint.get('description')}
            Target Market: {blueprint.get('targetMarket')}
            
            Return exactly 4-5 items for each category.
            Format as JSON with keys: strengths, weaknesses, opportunities, threats
            Each value should be an array of strings."""
            
            chat = LlmChat(
                api_key=llm_key,
                model="gpt-4o",
                system_message="You are a business analyst. Return only valid JSON."
            )
            
            response = await chat.send_async(message=UserMessage(text=prompt))
            
            # Try to parse JSON from response
            import json
            try:
                # Extract JSON from response
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                
                swot_data = json.loads(text.strip())
                return {
                    "strengths": swot_data.get("strengths", [])[:5],
                    "weaknesses": swot_data.get("weaknesses", [])[:5],
                    "opportunities": swot_data.get("opportunities", [])[:5],
                    "threats": swot_data.get("threats", [])[:5]
                }
            except Exception:
                return BlueprintService._get_fallback_swot(blueprint)
                
        except Exception as e:
            print(f"SWOT AI error: {e}")
            return BlueprintService._get_fallback_swot(blueprint)
    
    @staticmethod
    def _get_fallback_content(section_type: str, blueprint: dict) -> str:
        """Fallback content when AI is unavailable"""
        business_name = blueprint.get("businessName", "Your Business")
        industry = blueprint.get("industry", "your industry")
        
        fallbacks = {
            "executive_summary": f"""{business_name} is a innovative venture in the {industry} industry. Our mission is to deliver exceptional value to our customers through innovative solutions and outstanding service. With a focus on sustainable growth and customer satisfaction, we aim to establish ourselves as a market leader within the next 3-5 years.

Key highlights include:
- Strong value proposition addressing real market needs
- Experienced leadership team with industry expertise
- Scalable business model with multiple revenue streams
- Clear path to profitability and sustainable growth""",
            
            "market_analysis": f"""The {industry} market presents significant opportunities for growth. Our analysis indicates:

**Market Size & Growth**: The market continues to expand with strong fundamentals.

**Target Customer Segments**:
- Primary: Core customer base with immediate needs
- Secondary: Adjacent markets with growth potential

**Market Trends**:
- Digital transformation driving adoption
- Increasing demand for quality solutions
- Growing awareness of value-based services

**Key Success Factors**:
- Customer-centric approach
- Continuous innovation
- Strong brand positioning""",
            
            "products_services": f"""{business_name} offers a comprehensive suite of products and services:

**Core Offerings**:
- Primary product/service line
- Supporting services
- Premium tier options

**Key Features**:
- User-friendly design
- Scalable solutions
- Integration capabilities

**Competitive Advantages**:
- Superior quality
- Competitive pricing
- Excellent customer support""",
            
            "marketing_strategy": f"""Our marketing strategy focuses on building brand awareness and driving customer acquisition:

**Positioning**: Premium quality at competitive prices in the {industry} space.

**Marketing Channels**:
- Digital marketing (SEO, content, social media)
- Strategic partnerships
- Direct outreach and networking
- Referral programs

**Customer Acquisition Strategy**:
- Content marketing to establish thought leadership
- Targeted advertising campaigns
- Conversion optimization

**Brand Messaging**:
- Clear value proposition
- Trust and credibility building
- Customer success stories""",
            
            "operations_plan": f"""Our operations are designed for efficiency and scalability:

**Core Processes**:
- Service delivery workflow
- Quality assurance
- Customer support

**Technology Infrastructure**:
- Modern tech stack
- Scalable cloud infrastructure
- Security and compliance

**Resource Requirements**:
- Team structure and roles
- Key partnerships
- Vendor relationships

**Key Metrics**:
- Operational efficiency KPIs
- Quality metrics
- Customer satisfaction scores""",
            
            "financial_projections": f"""Financial projections for {business_name}:

**Revenue Model**:
- Multiple revenue streams
- Recurring revenue opportunities
- Upsell and cross-sell potential

**Cost Structure**:
- Fixed costs: Infrastructure, team, overhead
- Variable costs: Customer acquisition, delivery

**Break-even Analysis**:
- Projected break-even within 18-24 months
- Path to profitability clearly defined

**3-Year Projection Summary**:
- Year 1: Foundation building, initial revenue
- Year 2: Growth acceleration, market expansion
- Year 3: Scale and profitability""",
            
            "competitive_analysis": f"""Competitive landscape analysis for the {industry} market:

**Direct Competitors**:
- Established players with market share
- New entrants with innovative approaches

**Competitive Positioning**:
- Our unique differentiators
- Value proposition comparison
- Pricing strategy

**Market Share Opportunity**:
- Addressable market segments
- Growth potential

**Defensive Strategy**:
- Barriers to entry
- Customer retention focus
- Continuous innovation"""
        }
        
        return fallbacks.get(section_type, "Content for this section.")
    
    @staticmethod
    def _get_fallback_swot(blueprint: dict) -> dict:
        """Fallback SWOT when AI unavailable"""
        return {
            "strengths": [
                "Innovative approach to market needs",
                "Strong founding team expertise",
                "Scalable business model",
                "Clear value proposition"
            ],
            "weaknesses": [
                "Limited brand recognition initially",
                "Resource constraints as startup",
                "Need to build customer base",
                "Dependent on key team members"
            ],
            "opportunities": [
                "Growing market demand",
                "Digital transformation trends",
                "Partnership opportunities",
                "Geographic expansion potential"
            ],
            "threats": [
                "Competitive pressure",
                "Market volatility",
                "Regulatory changes",
                "Economic uncertainty"
            ]
        }
    
    @staticmethod
    def _generate_financial_projections(funding_goal: float, business_model: str) -> List[dict]:
        """Generate financial projections"""
        base_revenue = funding_goal * 0.3  # 30% of funding as first year revenue target
        
        projections = []
        for year in range(1, 4):
            growth_rate = 0.3 + (year * 0.15)  # 45%, 60%, 75% growth
            revenue = base_revenue * (1 + growth_rate) ** year
            expenses = revenue * (0.85 - (year * 0.1))  # Decreasing expense ratio
            
            projections.append({
                "year": year,
                "revenue": round(revenue, 2),
                "expenses": round(expenses, 2),
                "netIncome": round(revenue - expenses, 2),
                "growthRate": round(growth_rate * 100, 1)
            })
        
        return projections
