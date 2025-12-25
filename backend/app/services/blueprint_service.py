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
                session_id=f"blueprint-{section_type}",
                system_message="You are a professional business consultant creating business plan sections. Write clear, professional, and actionable content."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            # Handle both string response and object response
            return response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
            
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
                session_id="blueprint-swot",
                system_message="You are a business analyst. Return only valid JSON."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            
            # Try to parse JSON from response - handle both string and object response
            import json
            try:
                # Extract JSON from response
                text = response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
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
            
            "operations_plan": """Our operations are designed for efficiency and scalability:

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
    
    @staticmethod
    async def generate_document(data: dict) -> dict:
        """Generate business document using AI"""
        document_type = data.get("documentType", "quote")
        company_name = data.get("companyName", "Company")
        industry = data.get("industry", "")
        description = data.get("description", "")
        
        if not LLM_AVAILABLE:
            return {"content": BlueprintService._get_fallback_document(document_type, company_name)}
        
        try:
            llm = LlmChat(api_key=os.environ.get("EMERGENT_LLM_KEY", ""))
            
            # Professional preamble for all documents
            base_context = f"""You are a professional document drafting expert with expertise in UK business law and industry best practices.

COMPANY CONTEXT:
- Company Name: {company_name}
- Industry: {industry or 'General Business Services'}
- Description: {description or 'Professional services provider'}

CRITICAL REQUIREMENTS:
1. Write in perfect British English with correct grammar, spelling, and punctuation
2. Follow UK legal standards and industry best practices
3. Make it specific to the company - use the company name throughout, NOT generic placeholders
4. Structure with clear headings and professional formatting
5. Include relevant dates formatted as DD/MM/YYYY
6. Be comprehensive yet concise
7. Ensure legal validity where applicable

"""
            
            doc_prompts = {
                "quote": base_context + """Create a professional quotation/estimate document.

REQUIRED SECTIONS:
1. Company letterhead with full contact details
2. Quote reference number and date
3. Client information section
4. Detailed itemised pricing table with columns: Item, Description, Quantity, Unit Price (£), Total (£)
5. Subtotal, VAT (20%), and Grand Total
6. Validity period (typically 30 days)
7. Payment terms
8. Terms and conditions summary
9. Acceptance signature block

Make it look professional and ready to send to clients.""",
                
                "simple_contract": base_context + """Create a legally sound service agreement contract.

REQUIRED SECTIONS:
1. Agreement header with parties' details
2. Recitals (background/whereas clauses)
3. Definitions
4. Scope of Services
5. Fees and Payment Terms
6. Term and Termination
7. Confidentiality
8. Intellectual Property
9. Limitation of Liability
10. General Provisions (Force Majeure, Notices, Governing Law - England and Wales)
11. Signature blocks for both parties

Ensure it is enforceable under UK law.""",
                
                "proposal": base_context + """Create a compelling business proposal.

REQUIRED SECTIONS:
1. Cover page with company branding
2. Executive Summary
3. Understanding of Client Needs
4. Proposed Solution/Approach
5. Methodology and Timeline
6. Team/Resources
7. Investment Summary (pricing)
8. Why Choose Us (differentiators)
9. Case Studies/Testimonials (placeholder)
10. Next Steps and Call to Action
11. Terms and Conditions Summary

Make it persuasive and professional.""",
                
                "invoice_template": base_context + """Create a professional invoice template.

REQUIRED ELEMENTS:
1. Company logo/letterhead area
2. "INVOICE" header
3. Invoice number, date, and due date
4. Company VAT number (placeholder)
5. Bill To section
6. Itemised services/products table
7. Subtotal, VAT breakdown, Total Due
8. Payment methods and bank details section
9. Payment terms
10. Thank you note

Format for easy customisation.""",
                
                "privacy_policy": base_context + """Create a comprehensive GDPR and UK Data Protection Act 2018 compliant privacy policy.

REQUIRED SECTIONS:
1. Introduction and company identification
2. What information we collect
3. How we collect your information
4. How we use your information (legal bases)
5. Data sharing and third parties
6. International transfers
7. Data retention
8. Your rights under GDPR (access, rectification, erasure, portability, objection)
9. Cookies (brief, link to cookie policy)
10. Security measures
11. Children's privacy
12. Changes to this policy
13. Contact details and Data Protection Officer
14. Right to complain to ICO

Ensure full legal compliance.""",
                
                "cookie_notice": base_context + """Create a PECR and GDPR compliant cookie policy.

REQUIRED SECTIONS:
1. What are cookies
2. Types of cookies we use:
   - Strictly necessary
   - Performance/Analytics
   - Functionality
   - Targeting/Advertising
3. Specific cookies table (name, purpose, duration, type)
4. Third-party cookies
5. How to manage cookies (browser settings)
6. Consent management
7. Changes to policy
8. Contact information

Include practical guidance for users.""",
                
                "terms_conditions": base_context + """Create comprehensive terms and conditions.

REQUIRED SECTIONS:
1. Introduction and acceptance
2. Definitions
3. Services description
4. Account registration (if applicable)
5. Pricing and payment
6. Cancellation and refunds
7. User obligations
8. Intellectual property
9. Disclaimer and limitation of liability
10. Indemnification
11. Termination
12. Dispute resolution
13. Governing law (England and Wales)
14. Changes to terms
15. Contact information
16. Severability

Ensure enforceability under UK consumer law.""",
                
                "refund_policy": base_context + """Create a clear refund and returns policy compliant with UK Consumer Rights Act 2015.

REQUIRED SECTIONS:
1. Policy overview
2. Eligibility for refunds
3. Statutory rights (14-day cooling-off period for online sales)
4. How to request a refund
5. Refund process and timeline
6. Refund methods
7. Non-refundable items/services
8. Partial refunds
9. Exchanges
10. Faulty goods/services
11. Contact information

Be clear and customer-friendly while protecting the business.""",
                
                "employee_handbook": base_context + """Create a professional employee handbook.

REQUIRED SECTIONS:
1. Welcome message from leadership
2. Company overview, mission, and values
3. Employment policies
   - Equal opportunities
   - Recruitment and probation
   - Working hours and flexible working
4. Code of conduct
5. Leave policies (annual, sick, parental)
6. Benefits summary
7. Performance management
8. Disciplinary and grievance procedures
9. Health and safety
10. Data protection and confidentiality
11. IT and social media policy
12. Termination of employment
13. Acknowledgment form

Comply with UK employment law.""",
                
                "remote_work_policy": base_context + """Create a comprehensive remote/hybrid working policy.

REQUIRED SECTIONS:
1. Policy purpose and scope
2. Eligibility criteria
3. Application process
4. Working arrangements (hours, availability)
5. Workspace requirements
6. Equipment and expenses
7. Health and safety (DSE assessments)
8. Data security and confidentiality
9. Communication expectations
10. Performance management
11. Team collaboration
12. Return to office provisions
13. Policy review

Reflect modern working practices.""",
                
                "leave_policy": base_context + """Create a UK-compliant leave policy.

REQUIRED SECTIONS:
1. Annual leave entitlement (minimum 28 days including bank holidays)
2. Leave year and carry-over
3. Booking process
4. Sick leave and SSP
5. Maternity leave (52 weeks statutory)
6. Paternity leave (2 weeks statutory)
7. Shared parental leave
8. Adoption leave
9. Parental bereavement leave
10. Compassionate leave
11. Jury service
12. Time off for dependants
13. Unpaid leave

Ensure statutory compliance.""",
                
                "code_of_conduct": base_context + """Create a professional code of conduct.

REQUIRED SECTIONS:
1. Introduction and purpose
2. Core values and principles
3. Professional behaviour expectations
4. Equality, diversity, and inclusion
5. Anti-harassment and bullying
6. Conflicts of interest
7. Gifts and hospitality
8. Confidentiality
9. Use of company resources
10. Social media guidelines
11. Reporting concerns (whistleblowing)
12. Consequences of violations
13. Acknowledgment

Set clear expectations for all employees.""",
                
                "welcome_email": base_context + """Create a warm, professional welcome email template for new clients.

INCLUDE:
1. Personalised greeting
2. Expression of appreciation
3. Brief reminder of what they've signed up for
4. What to expect next (clear next steps)
5. Key contact information
6. Helpful resources or links
7. Invitation to reach out with questions
8. Professional sign-off

Make the client feel valued and informed.""",
                
                "follow_up_email": base_context + """Create a professional sales follow-up email template.

INCLUDE:
1. Personalised opening referencing previous interaction
2. Value reminder (what problem you solve)
3. Specific benefit or case study mention
4. Gentle handling of potential objections
5. Clear, specific call-to-action
6. Easy response mechanism
7. Professional sign-off
8. P.S. with added value or urgency

Be persuasive without being pushy.""",
                
                "thank_you_note": base_context + """Create a sincere client thank you note template.

INCLUDE:
1. Genuine expression of gratitude
2. Specific mention of what you're thanking them for
3. Recognition of the relationship value
4. Brief mention of positive outcomes or impact
5. Forward-looking statement
6. Offer of continued support
7. Warm, professional close

Make it personal and memorable.""",
                
                "meeting_agenda": base_context + """Create a professional meeting agenda template.

INCLUDE:
1. Meeting header (title, date, time, location/link)
2. Attendees list
3. Meeting objective
4. Agenda items with:
   - Topic
   - Presenter/Lead
   - Time allocation
5. Discussion points
6. Action items section
7. Next steps
8. Next meeting date placeholder
9. Notes section

Keep it structured and actionable."""
            }
            
            prompt = doc_prompts.get(document_type, base_context + f"Create a professional {document_type} document.")
            
            response = await llm.send_message(
                model="gpt-4o",
                messages=[UserMessage(content=prompt)]
            )
            
            text = response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
            
            return {"content": text.strip()}
            
        except Exception as e:
            print(f"Document generation error: {e}")
            return {"content": BlueprintService._get_fallback_document(document_type, company_name)}
    
    @staticmethod
    def _get_fallback_document(document_type: str, company_name: str) -> str:
        """Fallback documents when AI is unavailable"""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        templates = {
            "quote": f"""QUOTATION

{company_name}
Date: {date_str}
Quote #: [Number]
Valid Until: [Date]

TO:
[Client Name]
[Client Address]

DESCRIPTION OF SERVICES:

| Item | Description | Quantity | Unit Price | Total |
|------|-------------|----------|------------|-------|
| 1    | [Service]   | 1        | £0.00      | £0.00 |

Subtotal: £0.00
VAT (20%): £0.00
TOTAL: £0.00

Terms: Payment due within 30 days

Accepted by: _______________ Date: ___________""",

            "privacy_policy": f"""PRIVACY POLICY

Last Updated: {date_str}

{company_name} ("we", "us", or "our") is committed to protecting your privacy.

1. INFORMATION WE COLLECT
We collect information you provide directly to us.

2. HOW WE USE YOUR INFORMATION
We use the information to provide and improve our services.

3. INFORMATION SHARING
We do not sell or rent your personal information.

4. DATA SECURITY
We implement appropriate security measures.

5. YOUR RIGHTS
You have the right to access, correct, or delete your data.

6. CONTACT US
For questions, please contact us at: [email]""",

            "simple_contract": f"""SERVICE AGREEMENT

This Agreement is entered into on {date_str}

BETWEEN:
{company_name} ("Provider")
AND:
[Client Name] ("Client")

1. SERVICES
The Provider agrees to provide [describe services].

2. PAYMENT TERMS
[Payment details]

3. TERM
This agreement begins on [date] and continues until [date/completion].

4. TERMINATION
Either party may terminate with [X] days written notice.

5. CONFIDENTIALITY
Both parties agree to keep confidential information private.

SIGNATURES:

Provider: _______________ Date: ___________
Client: _______________ Date: ___________""",

            "welcome_email": f"""Subject: Welcome to {company_name}!

Dear [Client Name],

We're delighted to welcome you to {company_name}!

Thank you for choosing us. We're committed to providing you with exceptional service.

What happens next:
• [Step 1]
• [Step 2]
• [Step 3]

If you have any questions, don't hesitate to reach out.

Best regards,
The {company_name} Team"""
        }
        
        return templates.get(document_type, f"[{document_type.replace('_', ' ').title()} Template for {company_name}]")
