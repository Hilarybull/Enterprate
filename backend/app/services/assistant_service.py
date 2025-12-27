"""
Enterprate OS AI Assistant Service

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
    Enterprate OS AI Assistant — a verified, context-aware business 
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
        """
        # Patterns that are clearly outside business context
        non_business_patterns = [
            r'\b(recipe|cook|food|weather|sports|game|movie|music)',
            r'\b(joke|funny|entertainment|celebrity)',
            r'\b(personal|relationship|dating|health\s*advice)',
        ]
        
        message_lower = message.lower()
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
        base_identity = """You are the Enterprate OS AI Assistant — a verified, context-aware business intelligence and guidance system.

You are NOT a general-purpose chatbot. You are a decision-grade, trusted business companion.

CORE PRINCIPLES:
- Professional, precise, calm, non-speculative, enterprise-grade
- Never hallucinate company, legal, or compliance data
- Always distinguish between advisory guidance and verified intelligence
- Never provide legal advice as fact
- Never overstate certainty"""

        mode_instructions = {
            AssistantMode.ADVISORY: """
CURRENT MODE: ADVISORY (General Guidance)

RULES:
- Provide general business guidance only
- Do NOT make company-specific claims
- Do NOT assume information about filings, directors, or registration status
- Use phrases like "typically", "generally", "best practice suggests"
- Always include the disclosure: "This is general business guidance and is not based on live company records."
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
        return """I appreciate your question, but as the Enterprate OS AI Assistant, I'm specifically designed to help with business-related matters.

I can assist you with:

**Genesis AI** — Business idea validation, company formation, planning
**Navigator AI** — Finance, operations, compliance, tax
**Growth AI** — Marketing, sales, lead generation, expansion

How can I help you with your business today?"""


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
    Process a message through the Enterprate OS AI Assistant.
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
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
    
    # Create chat instance
    session_key = f"{user_id}_{session_id}"
    chat = LlmChat(
        api_key=api_key,
        session_id=session_key,
        system_message=system_prompt
    ).with_model("openai", "gpt-4o")
    
    # Send message
    response = await chat.send_message(UserMessage(text=message))
    
    # Format response with disclosures
    formatted_response = assistant.format_response(
        raw_response=response,
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
