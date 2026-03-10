"""
EnterprateAI AI Assistant Service

A decision-grade, verified, explainable business intelligence companion
that operates in three distinct modes: Advisory, Data-Backed, and Presentation.
"""
import os
import re
import json
import logging
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# =====================================================
# OPERATING MODES
# =====================================================
class AssistantMode(str, Enum):
    ADVISORY = "advisory"           # General business guidance
    DATA_BACKED = "data_backed"     # Verified Companies House data
    PRESENTATION = "presentation"   # Structured output mode


# =====================================================
# ENTERPRATE DOMAINS (Context Locking)
# =====================================================
class EnterpateDomain(str, Enum):
    GENESIS = "genesis"       # Idea, formation, planning
    NAVIGATOR = "navigator"   # Operations, finance, compliance
    GROWTH = "growth"         # Marketing, scale, expansion


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================
class AssistantRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    company_number: Optional[str] = None
    company_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AssistantResponse(BaseModel):
    response: str
    mode: str
    domain: str
    data_source: Optional[str] = None
    confidence: str = "standard"
    timestamp: str
    session_id: str


# =====================================================
# MODE DETECTION PATTERNS
# =====================================================
DATA_BACKED_TRIGGERS = [
    r'\b(check|verify|confirm|status|filing|registered|company\s*house)',
    r'\b(director|psc|person.*significant|shareholder|officer)',
    r'\b(sic\s*code|incorporation|registration|dissolved|active)',
    r'\b(compliance|annual\s*return|confirmation\s*statement)',
    r'\b(company\s*(number|no\.?|#)|([0-9]{7,8}))',
    r'\b(limited|ltd|plc|llp)\b',
]

PRESENTATION_TRIGGERS = [
    r'\b(summar|present|report|prepare.*for)',
    r'\b(investor|client|stakeholder|board)',
    r'\b(create.*report|explain.*clearly)',
    r'\b(format|structure|breakdown)',
]

# Domain detection patterns
GENESIS_PATTERNS = [
    r'\b(idea|concept|validate|start|formation|launch)',
    r'\b(business\s*plan|strategy|roadmap|model)',
    r'\b(register|incorporate|company\s*type)',
]

NAVIGATOR_PATTERNS = [
    r'\b(invoice|expense|finance|tax|vat|compliance)',
    r'\b(operation|workflow|task|document)',
    r'\b(receipt|payment|accounting)',
]

GROWTH_PATTERNS = [
    r'\b(marketing|lead|sales|growth|scale)',
    r'\b(campaign|promotion|social\s*media)',
    r'\b(customer|client\s*acquisition|expansion)',
]


class EnterprateAssistant:
    """
    EnterprateAI AI Assistant — a verified, context-aware business 
    intelligence and guidance system.
    """
    
    def __init__(self, api_key: str, workspace_id: str = None):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.current_mode = AssistantMode.ADVISORY
        self.current_domain = EnterpateDomain.NAVIGATOR
        self.companies_house_data = None
        
    def detect_mode(self, message: str, has_company_data: bool = False) -> AssistantMode:
        """
        Detect the appropriate operating mode based on the message content.
        
        Mode Priority:
        1. If company identifier provided -> DATA_BACKED
        2. If verification keywords -> DATA_BACKED
        3. If presentation keywords -> PRESENTATION (inherits current mode's data)
        4. Default -> ADVISORY
        """
        message_lower = message.lower()
        
        # Check for Presentation triggers FIRST (takes priority)
        for pattern in PRESENTATION_TRIGGERS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return AssistantMode.PRESENTATION
        
        # Check for Data-Backed triggers
        for pattern in DATA_BACKED_TRIGGERS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                # Don't trigger data-backed for generic "limited company" mentions
                # unless there's a specific company reference
                if 'limited' in message_lower or 'ltd' in message_lower:
                    # Only go data-backed if there's an actual company number or explicit verification request
                    if not re.search(r'\b[0-9]{7,8}\b', message) and not has_company_data:
                        if not re.search(r'(check|verify|confirm|status|filing)', message_lower):
                            continue
                return AssistantMode.DATA_BACKED
        
        # Check for company number pattern
        if re.search(r'\b[0-9]{7,8}\b', message):
            return AssistantMode.DATA_BACKED
            
        # Check if company data was explicitly provided
        if has_company_data:
            return AssistantMode.DATA_BACKED
        
        # Default to Advisory
        return AssistantMode.ADVISORY
    
    def detect_domain(self, message: str) -> EnterpateDomain:
        """
        Detect the Enterprate domain the message relates to.
        Every response must map to at least one domain.
        """
        message_lower = message.lower()
        
        scores = {
            EnterpateDomain.GENESIS: 0,
            EnterpateDomain.NAVIGATOR: 0,
            EnterpateDomain.GROWTH: 0,
        }
        
        for pattern in GENESIS_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                scores[EnterpateDomain.GENESIS] += 1
                
        for pattern in NAVIGATOR_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                scores[EnterpateDomain.NAVIGATOR] += 1
                
        for pattern in GROWTH_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                scores[EnterpateDomain.GROWTH] += 1
        
        # Return highest scoring domain, default to Navigator
        max_score = max(scores.values())
        if max_score == 0:
            return EnterpateDomain.NAVIGATOR
            
        for domain, score in scores.items():
            if score == max_score:
                return domain
                
        return EnterpateDomain.NAVIGATOR
    
    def is_valid_business_context(self, message: str) -> bool:
        """
        Check if the request falls within valid Enterprate business context.
        Platform questions about EnterprateAI are always valid.
        """
        message_lower = message.lower()
        
        # Platform-specific questions are always valid
        platform_patterns = [
            r'\b(enterprate|enterprateai|this platform|this app|this tool)',
            r'\b(how (do|can|does)|what (is|are|does)|where (is|can|do))',
            r'\b(feature|module|dashboard|workspace|setting)',
            r'\b(genesis|navigator|growth)\s*(ai)?',
        ]
        
        for pattern in platform_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        
        # Patterns that are clearly outside business context
        non_business_patterns = [
            r'\b(recipe|cook|food|weather|sports|game|movie|music)',
            r'\b(joke|funny|entertainment|celebrity)',
            r'\b(personal|relationship|dating|health\s*advice)',
        ]
        
        for pattern in non_business_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return False
        
        return True
    
    def get_mode_disclosure(self, mode: AssistantMode, data_source: str = None) -> str:
        """
        Generate the required disclosure based on the operating mode.
        """
        if mode == AssistantMode.ADVISORY:
            return "📋 *Advisory Mode* — This is general business guidance and is not based on live company records."
        
        elif mode == AssistantMode.DATA_BACKED:
            timestamp = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
            if data_source:
                return f"✓ *Data-Backed Mode* — Using {data_source} records as of {timestamp}."
            return f"✓ *Data-Backed Mode* — Using verified company records as of {timestamp}."
        
        elif mode == AssistantMode.PRESENTATION:
            return "📊 *Presentation Mode* — Structured output for stakeholder communication."
        
        return ""
    
    def get_domain_context(self, domain: EnterpateDomain) -> str:
        """
        Get helpful context about the Enterprate domain.
        """
        contexts = {
            EnterpateDomain.GENESIS: "This relates to **Genesis AI** — idea discovery, validation, company formation, and business planning.",
            EnterpateDomain.NAVIGATOR: "This relates to **Navigator AI** — operations, finance, compliance, and day-to-day business management.",
            EnterpateDomain.GROWTH: "This relates to **Growth AI** — marketing, lead generation, sales, and business expansion.",
        }
        return contexts.get(domain, "")
    
    def build_system_prompt(self, mode: AssistantMode, domain: EnterpateDomain, company_data: dict = None) -> str:
        """
        Build the system prompt based on the current operating mode and domain.
        """
        base_identity = """You are the EnterprateAI AI Assistant — a verified, context-aware business intelligence and guidance system built into the EnterprateAI platform.

You are NOT a general-purpose chatbot. You are a decision-grade, trusted business companion that helps entrepreneurs and businesses succeed.

=== ENTERPRATEAI PLATFORM KNOWLEDGE ===

EnterprateAI is an AI-powered operating system for businesses, designed to help entrepreneurs start, run, and grow their companies. The platform consists of three core AI modules:

**1. GENESIS AI (Idea Discovery & Formation)**
- Business Idea Validation: AI-powered validation reports with market analysis, competitor insights, and feasibility scores
- Business Registration: UK company formation with Companies House integration, name availability checking
- Business Blueprint: Generate comprehensive business plans, pitch decks, and strategy documents
- Entity Type Selection: Guidance on choosing between Ltd, LLP, PLC, etc.

**2. NAVIGATOR AI (Operations & Compliance)**
- Finance Automation: Invoice generation, expense tracking, receipt scanning with OCR
- Compliance Management: Automated reminders for confirmation statements, annual accounts, VAT returns
- Document Management: AI-organized business document storage
- Tax Planning: VAT calculation, corporation tax guidance
- Operations Dashboard: Real-time business metrics and KPIs

**3. GROWTH AI (Marketing & Expansion)**
- AI Website Builder: Generate professional landing pages using AIDA framework, deploy to Netlify/Vercel
- Lead Generation: Capture and manage leads from generated websites
- Social Media Management: Schedule posts to LinkedIn, Twitter, Facebook, Instagram
- Campaign Automation: Create automated marketing workflows with triggers and actions
- A/B Testing: Test different marketing variants to optimize conversions
- Website Analytics: Track visits, conversions, and user behavior

**KEY PLATFORM FEATURES:**
- Workspace System: Users can create multiple workspaces for different businesses/projects
- Team Collaboration: Invite team members with role-based access (Owner, Admin, Member, Viewer)
- Real-Time Notifications: WebSocket-powered live notifications for leads, deployments, and events
- Custom Domains: Connect custom domains to deployed websites with DNS verification
- Intelligence Graph: Visual knowledge graph showing business connections and insights
- Multi-language Support: Generate content in multiple languages
- Quick Templates: 15+ industry-specific website templates (SaaS, Consulting, E-commerce, etc.)

**INTEGRATIONS:**
- Companies House API: Real-time UK company data verification
- OpenAI GPT-4o: Powers AI content generation and chat
- Google Gemini: Used for AI Website Builder
- Netlify/Vercel: One-click website deployment
- Google OAuth: Social login authentication

**PRICING & ACCESS:**
- The platform is currently in beta/early access
- Users can create workspaces and access all features
- Website deployments support custom domains

=== END PLATFORM KNOWLEDGE ===

CORE PRINCIPLES:
- Professional, precise, calm, non-speculative, enterprise-grade
- Never hallucinate company, legal, or compliance data
- Always distinguish between advisory guidance and verified intelligence
- Never provide legal advice as fact
- Never overstate certainty
- When asked about EnterprateAI features, provide accurate information based on the platform knowledge above
- If asked about a feature that doesn't exist, clearly state it's not currently available rather than making up functionality"""

        mode_instructions = {
            AssistantMode.ADVISORY: """
CURRENT MODE: ADVISORY (General Guidance)

RULES:
- Provide general business guidance only
- Do NOT make company-specific claims
- Do NOT assume information about filings, directors, or registration status
- Use phrases like "typically", "generally", "best practice suggests"
- Always include the disclosure: "This is general business guidance and is not based on live company records."
- When explaining EnterprateAI features, be accurate and helpful
""",
            AssistantMode.DATA_BACKED: """
CURRENT MODE: DATA-BACKED (Verified Intelligence)

RULES:
- Use ONLY verified data from the provided company records
- State exact values (dates, statuses, names) when available
- If data is missing or unavailable, explicitly say so
- NEVER infer, assume, or guess information
- Always cite the data source (e.g., "According to Companies House records...")
- Include timestamp of data retrieval
""",
            AssistantMode.PRESENTATION: """
CURRENT MODE: PRESENTATION (Structured Output)

RULES:
- Use clear headings, bullet points, and structured formatting
- Maintain data integrity from the underlying mode
- Format for stakeholder communication (investor, client, board)
- Include executive summary where appropriate
- Use markdown formatting for clarity
"""
        }

        domain_context = {
            EnterpateDomain.GENESIS: """
DOMAIN: GENESIS AI (Formation & Planning)
Focus areas: Business idea validation, market research, company formation, business planning, competitive analysis, entity type selection.""",
            EnterpateDomain.NAVIGATOR: """
DOMAIN: NAVIGATOR AI (Operations & Compliance)
Focus areas: Finance automation, invoicing, expense tracking, compliance management, tax planning, document management, business operations.""",
            EnterpateDomain.GROWTH: """
DOMAIN: GROWTH AI (Marketing & Expansion)
Focus areas: Lead generation, marketing campaigns, sales strategies, customer acquisition, social media management, business growth."""
        }

        response_structure = """
RESPONSE STRUCTURE (Follow for all substantive responses):
1. **Explain** — What the data or principle says
2. **Interpret** — What it means in practice
3. **Recommend** — What the user should do
4. **Action** — How Enterprate can help next

DATA PRIORITY ORDER:
1. Companies House API (when applicable)
2. Enterprate Intelligence Graph
3. User Workspace / Project Data
4. General business knowledge (clearly labelled)
"""

        prompt = f"{base_identity}\n\n{mode_instructions.get(mode, '')}\n\n{domain_context.get(domain, '')}\n\n{response_structure}"
        
        # Add company data context if available
        if company_data and mode == AssistantMode.DATA_BACKED:
            prompt += f"""

VERIFIED COMPANY DATA (Use this data in your response):
```json
{json.dumps(company_data, indent=2, default=str)}
```
"""
        
        return prompt
    
    def format_response(self, raw_response: str, mode: AssistantMode, domain: EnterpateDomain, data_source: str = None) -> str:
        """
        Format the response with appropriate disclosures and context.
        """
        disclosure = self.get_mode_disclosure(mode, data_source)
        domain_context = self.get_domain_context(domain)
        
        # Build formatted response
        formatted = f"{disclosure}\n\n{raw_response}"
        
        # Add domain context at the end if helpful
        if domain_context:
            formatted += f"\n\n---\n🏢 {domain_context}"
        
        return formatted
    
    def get_out_of_context_response(self) -> str:
        """
        Response for requests outside business context.
        """
        return """I appreciate your question, but as the EnterprateAI AI Assistant, I'm specifically designed to help with business-related matters.

I can assist you with:

**Genesis AI** — Business idea validation, company formation, planning
**Navigator AI** — Finance, operations, compliance, tax
**Growth AI** — Marketing, sales, lead generation, website building, expansion

I can also answer questions about the **EnterprateAI platform** itself — features, how to use specific modules, and best practices.

How can I help you with your business today?"""


def _ctxv(data: Dict[str, Any], key: str, default: str = "") -> str:
    value = (data or {}).get(key)
    if value is None:
        return default
    return str(value)


def _offline_answer(message: str, workspace_context: dict = None) -> str:
    ctx = workspace_context or {}
    idea_input = ctx.get("ideaInput", ctx)
    report = ctx.get("report", {})
    det = report.get("deterministicSummary", {})
    metrics = det.get("metrics", {})
    factors = det.get("marketContext", {}).get("factors", {})
    score = det.get("validationScore", "N/A")
    problem = _ctxv(idea_input, "problemSolved", "the core customer pain")
    audience = _ctxv(idea_input, "targetAudience", _ctxv(idea_input, "customerSegment", "target users"))
    delivery = _ctxv(idea_input, "deliveryModel", "service")
    how = _ctxv(idea_input, "howItWorks", "deliver value through a repeatable process")
    m = (message or "").lower()

    if "problem" in m and "solve" in m:
        return f"It solves {problem} for {audience}, using a {delivery} approach."
    if "market" in m and ("opportunity" in m or "big" in m or "size" in m):
        d = factors.get("demand", "N/A")
        c = factors.get("competition", "N/A")
        return f"Current market signal is demand {d}/100 and competition {c}/100, with overall validation score {score}/100."
    if "revenue" in m or "money" in m or "price" in m:
        rev = metrics.get("monthlyRevenue", 0)
        net = metrics.get("monthlyNet", 0)
        return f"Projected monthly revenue is {rev} and monthly net is {net}. This should be validated against real conversion and retention data."
    if "risk" in m:
        margin = metrics.get("contributionMarginPct", 0)
        return f"Key risks are execution capacity, acquisition cost pressure, and margin stability (current margin: {margin}%)."
    if "build" in m or "hard" in m or "difficult" in m:
        return f"Execution depends on delivering consistently at planned capacity. Current operating approach: {how}."

    return (
        f"Based on your report, this idea targets {audience} and addresses {problem}. "
        f"Current validation score is {score}/100. Ask about market, risks, pricing, or execution and I will break it down."
    )


# =====================================================
# COMPANIES HOUSE DATA FETCHER
# =====================================================
async def fetch_companies_house_data(company_number: str = None, company_name: str = None, api_key: str = None) -> Optional[dict]:
    """
    Fetch verified company data from Companies House API.
    """
    if not api_key:
        api_key = os.environ.get("COMPANIES_HOUSE_API_KEY")
    
    if not api_key:
        return None
    
    import httpx
    import base64
    
    auth_header = base64.b64encode(f"{api_key}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    
    try:
        async with httpx.AsyncClient() as client:
            if company_number:
                # Direct lookup by company number
                response = await client.get(
                    f"https://api.company-information.service.gov.uk/company/{company_number}",
                    headers=headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "company_name": data.get("company_name"),
                        "company_number": data.get("company_number"),
                        "company_status": data.get("company_status"),
                        "type": data.get("type"),
                        "date_of_creation": data.get("date_of_creation"),
                        "registered_office_address": data.get("registered_office_address"),
                        "sic_codes": data.get("sic_codes", []),
                        "accounts": data.get("accounts", {}),
                        "confirmation_statement": data.get("confirmation_statement", {}),
                        "has_charges": data.get("has_charges", False),
                        "has_insolvency_history": data.get("has_insolvency_history", False),
                        "data_source": "Companies House API",
                        "retrieved_at": datetime.now(timezone.utc).isoformat()
                    }
            
            elif company_name:
                # Search by name
                response = await client.get(
                    "https://api.company-information.service.gov.uk/search/companies",
                    params={"q": company_name, "items_per_page": 5},
                    headers=headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    if items:
                        return {
                            "search_results": [
                                {
                                    "company_name": item.get("title"),
                                    "company_number": item.get("company_number"),
                                    "company_status": item.get("company_status"),
                                    "address_snippet": item.get("address_snippet"),
                                    "date_of_creation": item.get("date_of_creation")
                                }
                                for item in items
                            ],
                            "data_source": "Companies House API",
                            "retrieved_at": datetime.now(timezone.utc).isoformat()
                        }
    
    except Exception as e:
        logger.error(f"Companies House API error: {e}")
    
    return None


# =====================================================
# MAIN CHAT FUNCTION
# =====================================================
async def process_assistant_message(
    message: str,
    session_id: str,
    user_id: str,
    company_number: str = None,
    company_name: str = None,
    workspace_context: dict = None
) -> AssistantResponse:
    """
    Process a message through the EnterprateAI AI Assistant.
    """
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        has_emergent_sdk = True
    except ImportError:
        LlmChat = None
        UserMessage = None
        has_emergent_sdk = False
    
    claude_key = os.environ.get("CLAUDE_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    emergent_key = os.environ.get("EMERGENT_LLM_KEY")
    api_key = claude_key or gemini_key or emergent_key
    if not api_key:
        raise ValueError("AI service not configured")
    
    assistant = EnterprateAssistant(api_key)
    
    # Check if request is within business context
    if not assistant.is_valid_business_context(message):
        return AssistantResponse(
            response=assistant.get_out_of_context_response(),
            mode=AssistantMode.ADVISORY.value,
            domain=EnterpateDomain.NAVIGATOR.value,
            data_source=None,
            confidence="standard",
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id
        )
    
    # Detect operating mode and domain
    has_company_data = bool(company_number or company_name)
    mode = assistant.detect_mode(message, has_company_data)
    domain = assistant.detect_domain(message)
    
    # Fetch Companies House data if in Data-Backed mode
    company_data = None
    data_source = None
    
    if mode == AssistantMode.DATA_BACKED:
        if company_number or company_name:
            company_data = await fetch_companies_house_data(
                company_number=company_number,
                company_name=company_name
            )
            if company_data:
                data_source = "Companies House"
        
        # If no company data available but data-backed mode triggered, 
        # inform user we need company identifier
        if not company_data and not company_number and not company_name:
            return AssistantResponse(
                response="""To provide verified company information, I need a company identifier.

**Please provide one of the following:**
- Company registration number (e.g., 12345678)
- Exact company name

Once you provide this, I can access Companies House records to give you accurate, verified data.

*Alternatively, if you'd like general guidance without specific company data, just ask and I'll provide advisory information.*""",
                mode=AssistantMode.ADVISORY.value,
                domain=domain.value,
                data_source=None,
                confidence="standard",
                timestamp=datetime.now(timezone.utc).isoformat(),
                session_id=session_id
            )
    
    # Build system prompt
    system_prompt = assistant.build_system_prompt(mode, domain, company_data)
    
    # Generate response text using available AI SDK.
    response = None
    ai_error = None
    if has_emergent_sdk:
        try:
            session_key = f"{user_id}_{session_id}"
            provider = "anthropic" if claude_key else ("google" if gemini_key else "openai")
            model = "claude-sonnet-4-20250514" if claude_key else ("gemini-2.0-flash" if gemini_key else "gpt-4o")
            chat = LlmChat(
                api_key=api_key,
                session_id=session_key,
                system_message=system_prompt
            ).with_model(provider, model)
            # Use SDK-compatible message field name. Keep fallback for older SDK variants.
            try:
                response = await chat.send_message(UserMessage(content=message))
            except TypeError:
                response = await chat.send_message(UserMessage(text=message))
        except Exception as e:
            logger.warning(f"Primary SDK chat failed, trying provider fallback: {e}")
            ai_error = str(e)
            response = None

    if response is None and gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"{system_prompt}\n\nUser message:\n{message}"
            gemini_response = model.generate_content(prompt)
            response = getattr(gemini_response, "text", None) or str(gemini_response)
        except Exception as e:
            logger.error(f"Gemini fallback error: {e}")
            ai_error = str(e)
            response = None

    if response is None:
        offline = _offline_answer(message, workspace_context)
        if ai_error and ("429" in ai_error or "quota" in ai_error.lower()):
            offline = (
                "Live AI is temporarily unavailable due to API quota limits. "
                "Showing a report-based instant answer instead.\n\n" + offline
            )
        return AssistantResponse(
            response=offline,
            mode=AssistantMode.ADVISORY.value,
            domain=domain.value,
            data_source="report_context_fallback",
            confidence="standard",
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id
        )
    
    # Format response with disclosures
    response_text = response.content if hasattr(response, "content") else str(response)
    formatted_response = assistant.format_response(
        raw_response=response_text,
        mode=mode,
        domain=domain,
        data_source=data_source
    )
    
    # Determine confidence level
    confidence = "verified" if mode == AssistantMode.DATA_BACKED and company_data else "standard"
    
    return AssistantResponse(
        response=formatted_response,
        mode=mode.value,
        domain=domain.value,
        data_source=data_source,
        confidence=confidence,
        timestamp=datetime.now(timezone.utc).isoformat(),
        session_id=session_id
    )
