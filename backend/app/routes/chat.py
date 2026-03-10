"""
Chat routes for EnterprateAI AI Assistant

A decision-grade, verified, explainable business intelligence companion
that operates in three distinct modes: Advisory, Data-Backed, and Presentation.
"""
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.core.security import get_current_user
from app.core.database import get_db
from app.services.market_data_service import MarketDataService
from app.services.macro_data_service import MacroDataService
from app.services.assistant_service import (
    process_assistant_message,
    AssistantMode,
    EnterpateDomain
)

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory chat sessions with enhanced metadata
chat_sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    company_number: Optional[str] = None
    company_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    mode: str = "advisory"
    domain: str = "navigator"
    data_source: Optional[str] = None
    confidence: str = "standard"
    timestamp: str = None


class SuggestRequest(BaseModel):
    field: str
    context: Optional[Dict[str, Any]] = None


class SuggestResponse(BaseModel):
    suggestion_id: str
    suggestion: str
    provider: str = "fallback"
    data_source: Optional[str] = None
    grounding_summary: Optional[str] = None


class SuggestFeedbackRequest(BaseModel):
    suggestion_id: str
    field: str
    feedback: str  # accept | edit | reject
    suggested_text: Optional[str] = None
    final_text: Optional[str] = None
    provider: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


def _ctx(context: Dict[str, Any], key: str, default: str = "not provided") -> str:
    value = context.get(key)
    if value is None or value == "":
        return default
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else default
    return str(value)


def _ctx_any(context: Dict[str, Any], keys: List[str], default: str = "not provided") -> str:
    for k in keys:
        value = context.get(k)
        if value is None or value == "":
            continue
        if isinstance(value, list):
            return ", ".join(str(v) for v in value) if value else default
        return str(value)
    return default


def _segment_phrase(segment: str) -> str:
    s = (segment or "").strip().lower()
    if s == "freelancers":
        return "freelance professionals"
    if s == "households":
        return "households and individual consumers"
    if s in {"small offices", "smes"}:
        return "small business owners and operations leads"
    return segment or "target customers"


def _market_phrase(target_market: str) -> str:
    tm = (target_market or "").strip().upper()
    if tm in {"B2B", "B2C", "B2G"}:
        return f"({tm})"
    return ""


def _solution_use_case(context: Dict[str, Any]) -> str:
    text = " ".join([
        _ctx_any(context, ["whatYouAreBuilding", "ideaDescription"], ""),
        _ctx(context, "serviceType", ""),
        _ctx(context, "businessType", ""),
        _ctx(context, "industry", ""),
        _ctx(context, "subIndustry", ""),
    ]).lower()
    if any(k in text for k in ["mobile", "app", "ios", "android"]):
        return "building and shipping mobile apps"
    if any(k in text for k in ["website", "web", "landing page"]):
        return "building and managing websites"
    if any(k in text for k in ["marketing", "ads", "seo"]):
        return "running client marketing campaigns"
    if any(k in text for k in ["bookkeeping", "accounting", "finance"]):
        return "handling routine finance operations"
    return "delivering work to clients faster"


def _infer_primary_user_group(context: Dict[str, Any]) -> str:
    text = " ".join([
        _ctx_any(context, ["whatYouAreBuilding", "ideaDescription"], ""),
        _ctx(context, "serviceType", ""),
        _ctx(context, "businessType", ""),
    ]).lower()
    if any(k in text for k in ["developer", "coding", "programmer", "software engineer"]):
        return "developers"
    if any(k in text for k in ["designer", "ui", "ux"]):
        return "designers"
    if any(k in text for k in ["marketer", "seo", "ads", "campaign"]):
        return "marketers"
    if any(k in text for k in ["student", "teacher", "school", "learning"]):
        return "students and educators"
    return "users"


def _derive_market_issues(context: Dict[str, Any], market_profile: Dict[str, Any], macro_profile: Dict[str, Any]) -> List[str]:
    """Build deterministic issue cues from service + market + macro context."""
    issues: List[str] = []
    factors = market_profile.get("factors", {})
    demand = int(factors.get("demand", 50))
    competition = int(factors.get("competition", 50))
    cpc = int(factors.get("cpcPressure", 50))
    macro = int(macro_profile.get("score", 50))
    problem_type = [str(p).lower() for p in (context.get("problemType") or [])]
    industry = _ctx(context, "subIndustry", _ctx(context, "industry", "this industry")).lower()

    if demand >= 70:
        issues.append("Demand appears active; speed-to-market and differentiation matter.")
    if competition >= 70:
        issues.append("Competition is high; alternatives already exist and comparison shopping is common.")
    if cpc >= 70:
        issues.append("Customer acquisition cost pressure is high; low-friction channels are important.")
    if macro <= 45:
        issues.append("Macro conditions are tight; buyers may delay or reduce spending.")

    if "time" in problem_type:
        issues.append(f"In {industry}, long turnaround times create workflow bottlenecks.")
    if "cost" in problem_type:
        issues.append(f"In {industry}, rising operating costs are squeezing margins for buyers.")
    if "quality" in problem_type:
        issues.append(f"In {industry}, inconsistent delivery quality drives churn and rework.")
    if "reliability" in problem_type:
        issues.append(f"In {industry}, service inconsistency reduces trust and retention.")
    if "compliance" in problem_type:
        issues.append(f"In {industry}, compliance gaps create legal and financial risk.")

    if not issues:
        issues.append("Customers need faster, clearer outcomes with predictable delivery and pricing.")
    return issues[:5]


def _build_suggestion_prompt(
    field: str,
    context: Dict[str, Any],
    market_profile: Dict[str, Any],
    macro_profile: Dict[str, Any],
    issues: List[str]
) -> str:
    expected = _ctx(context, "expectedResult", "clear, specific, and actionable for validation scoring")
    issues_block = " | ".join(issues)
    market_factors = market_profile.get("factors", {})
    macro_raw = macro_profile.get("raw", {})
    grounding = (
        f"GROUNDING DATA (must use): "
        f"market_source={market_profile.get('source', 'baseline_rules')}; "
        f"demand={market_factors.get('demand', 'na')}; competition={market_factors.get('competition', 'na')}; "
        f"cpc_pressure={market_factors.get('cpcPressure', 'na')}; "
        f"macro_source={macro_profile.get('source', 'fallback')}; macro_score={macro_profile.get('score', 'na')}; "
        f"gdp_growth={macro_raw.get('gdpGrowth', 'na')}; inflation={macro_raw.get('inflation', 'na')}; "
        f"unemployment={macro_raw.get('unemployment', 'na')}; policy_rate={macro_raw.get('policyRate', 'na')}; "
        f"current_issues={issues_block}."
    )

    if field == "targetAudience":
        market_source = market_profile.get("source", "baseline_rules")
        mf = market_profile.get("factors", {})
        macro_source = macro_profile.get("source", "fallback")
        mr = macro_profile.get("raw", {})
        return (
            "You are a startup market segmentation expert specializing in identifying realistic early adopters for new digital products.\n\n"
            "First silently think about the structure:\n"
            "1. Identify the role or segment\n"
            "2. Identify the primary user group\n"
            "3. Identify the use-case\n"
            "4. Identify the location\n"
            "5. Identify a concrete operational pain\n\n"
            "Then write ONE target audience statement.\n\n"
            "### Output Rules\n"
            "- Maximum 28 words\n"
            "- Plain text only\n"
            "- One sentence\n"
            "- No explanations\n"
            "- No filler words\n"
            "- No extra punctuation\n"
            "- Do not mention the idea name\n\n"
            "### Forbidden vague phrases\n"
            "- busy owners\n"
            "- professionals\n"
            "- users\n"
            "- companies\n"
            "- faster turnaround\n"
            "- dependable quality\n\n"
            "### Required Structure\n"
            "role or segment + primary user group + use case + location + concrete pain\n\n"
            "### Additional Constraints\n"
            "- Use idea_description to infer the primary user group\n"
            "- Pain must be operational and measurable\n"
            "- If customer_segment = freelancers avoid B2B or decision-maker phrasing\n"
            "- Avoid generic labels like 'in technology'\n"
            "- Do not exceed 28 words\n\n"
            "### Grounding Data\n"
            f"market_source={market_source}\n"
            f"demand={mf.get('demand', 'na')}\n"
            f"competition={mf.get('competition', 'na')}\n"
            f"cpc_pressure={mf.get('cpcPressure', 'na')}\n\n"
            f"macro_source={macro_source}\n"
            f"macro_score={macro_profile.get('score', 'na')}\n"
            f"gdp_growth={mr.get('gdpGrowth', 'na')}\n"
            f"inflation={mr.get('inflation', 'na')}\n"
            f"unemployment={mr.get('unemployment', 'na')}\n"
            f"policy_rate={mr.get('policyRate', 'na')}\n"
            f"current_issues={issues_block}\n\n"
            "### Business Context\n"
            f"business_name={_ctx_any(context,['businessName','ideaName'])}\n"
            f"idea_description={_ctx_any(context,['whatYouAreBuilding','ideaDescription'])}\n"
            f"industry={_ctx(context,'industry')}\n"
            f"location={_ctx(context,'targetLocation')}\n"
            f"customer_segment={_ctx(context,'customerSegment')}\n"
            f"target_market={_ctx(context,'targetMarket')}\n\n"
            "### Self Check Before Returning\n"
            "- Is the statement 28 words or less?\n"
            "- Does it follow the required structure?\n"
            "- Is the pain specific and realistic?\n\n"
            "Return only the final statement."
        )
    if field == "problemSolved":
        market_source = market_profile.get("source", "baseline_rules")
        mf = market_profile.get("factors", {})
        macro_source = macro_profile.get("source", "fallback")
        mr = macro_profile.get("raw", {})
        return (
            "You are a startup problem discovery analyst and market validation expert.\n"
            "Your job is to translate business context and market signals into a clear, realistic customer problem statement.\n\n"
            "First silently determine:\n"
            "1. The specific customer pain\n"
            "2. The real-world impact of that pain\n"
            "3. Any relevant market issue influencing the problem\n\n"
            "Then write ONE customer problem statement.\n\n"
            "### Output Rules\n"
            "- Maximum 30 words\n"
            "- Plain text only\n"
            "- One sentence\n"
            "- No explanations\n"
            "- Do not mention the idea name\n\n"
            "### Required Structure\n"
            "customer pain + real-world impact + optional link to current market issue\n\n"
            "### Constraints\n"
            "- Clearly state the core pain\n"
            "- Clearly state the consequence or business impact\n"
            "- Align with the provided audience\n"
            "- Consider frequency, urgency, and existing alternatives\n"
            "- Avoid vague terms such as:\n"
            "  challenges\n"
            "  inefficiencies\n"
            "  problems\n"
            "  difficulties\n"
            "- Be concrete and operational\n\n"
            "### Grounding Data\n"
            f"market_source={market_source}\n"
            f"demand={mf.get('demand','na')}\n"
            f"competition={mf.get('competition','na')}\n"
            f"cpc_pressure={mf.get('cpcPressure','na')}\n\n"
            f"macro_source={macro_source}\n"
            f"macro_score={macro_profile.get('score','na')}\n"
            f"gdp_growth={mr.get('gdpGrowth','na')}\n"
            f"inflation={mr.get('inflation','na')}\n"
            f"unemployment={mr.get('unemployment','na')}\n"
            f"policy_rate={mr.get('policyRate','na')}\n"
            f"current_issues={issues_block}\n\n"
            "### Business Context\n"
            f"audience={_ctx(context,'targetAudience')}\n"
            f"problem_type={_ctx(context,'problemType')}\n"
            f"frequency={_ctx(context,'problemFrequency')}\n"
            f"urgency={_ctx(context,'urgencyLevel')}\n"
            f"alternatives={_ctx(context,'currentAlternatives')}\n"
            f"expected_result={expected}\n\n"
            "### Self Check Before Returning\n"
            "- Is the statement 30 words or fewer?\n"
            "- Does it clearly state pain and impact?\n"
            "- Does it align with the audience?\n\n"
            "Return only the final customer problem statement."
        )
    if field == "serviceType":
        return (
            "Suggest ONE concise service name, plain text only, max 8 words.\n"
            f"{grounding}\n"
            f"business_name={_ctx_any(context,['businessName','ideaName'])}; "
            f"what_you_are_building={_ctx_any(context,['whatYouAreBuilding','ideaDescription'])}; "
            f"industry={_ctx(context,'industry')}; "
            f"business_type={_ctx(context,'businessType')}; audience={_ctx(context,'targetAudience')}; "
            f"problem={_ctx(context,'problemSolved')}; pricing_model={_ctx(context,'pricingModel')}; "
            f"delivery_unit={_ctx(context,'deliverableUnit')}; expected_result={expected}."
        )
    # howItWorks
    return (
        "You are a startup operations analyst and business model designer.\n"
        "Your job is to explain how a new service actually operates in the real world using the provided business data.\n\n"
        "First silently determine:\n"
        "1. How the service is delivered\n"
        "2. How customers access or receive the service\n"
        "3. Whether demand fits operational capacity\n"
        "4. Whether pricing and volume are realistic\n\n"
        "Then write ONE short 'how it works' description.\n\n"
        "### Output Rules\n"
        "- Exactly 2 sentences\n"
        "- Maximum 45 words total\n"
        "- Plain text only\n"
        "- No bullet points\n"
        "- No marketing language\n"
        "- No explanations outside the sentences\n\n"
        "### Content Requirements\n"
        "- Explain how customers receive the service\n"
        "- Explain how the app is designed to work in practice\n"
        "- Include a simple user flow from input to output\n"
        "- Reflect the delivery model and pricing structure\n"
        "- Be operationally realistic\n"
        "- Ensure demand fits staff capacity\n"
        "- Align with current market conditions\n\n"
        "### Grounding Data\n"
        f"{grounding}\n\n"
        "### Business Operations\n"
        f"service_name={_ctx(context,'serviceType')}\n"
        f"delivery_model={_ctx(context,'deliveryModel')}\n"
        f"pricing_model={_ctx(context,'pricingModel')}\n"
        f"unit_price={_ctx(context,'priceAmount')}\n"
        f"units_per_month={_ctx(context,'expectedUnitsPerMonth')}\n"
        f"customers={_ctx(context,'expectedCustomers')}\n"
        f"capacity_per_staff={_ctx(context,'capacityPerStaffPerMonth')}\n"
        f"team_count={_ctx(context,'staffCount')}\n"
        f"expected_result={expected}\n\n"
        "### Self Check Before Returning\n"
        "- Exactly two sentences?\n"
        "- 45 words or fewer?\n"
        "- Operationally realistic?\n"
        "- Capacity >= demand?\n\n"
        "Return only the final two sentences."
    )


def _fallback_suggestion(field: str, context: Optional[Dict[str, Any]] = None) -> str:
    context = context or {}
    audience = str(context.get("targetAudience") or "").strip() or "small businesses needing reliable support"
    service = str(context.get("serviceType") or "").strip() or "a clear, outcome-focused service"
    industry = _ctx(context, "subIndustry", _ctx(context, "industry", "business operations"))
    location = _ctx(context, "targetLocation", "the target market")
    customer_segment = _ctx(context, "customerSegment", "SMEs")
    target_market = _ctx(context, "targetMarket", "")
    problem_type = _ctx(context, "problemType", "time and quality")
    segment_text = _segment_phrase(customer_segment)
    market_text = _market_phrase(target_market)
    use_case = _solution_use_case(context)
    primary_group = _infer_primary_user_group(context)

    if field == "targetAudience":
        if (customer_segment or "").strip().lower() == "freelancers":
            return (
                f"Freelancers and solo founders in {location} {market_text} "
                f"who are {primary_group} and are {use_case}, losing billable hours from app crashes, slow publishing, and repeated rework."
            )
        return (
            f"{segment_text} in {location} {market_text} "
            f"who are {primary_group} and are {use_case}, losing revenue from missed deadlines, repeat fixes, and unstable delivery."
        )

    fallbacks = {
        "problemSolved": (
            f"{audience} face recurring {problem_type} issues due to inconsistent providers, "
            f"causing delays, rework, and higher operating costs."
        ),
        "serviceType": f"{industry} Performance Support Service",
        "howItWorks": (
            f"We diagnose the customer requirement, deliver {service} through a repeatable weekly workflow, "
            f"and track outcomes with clear milestones and progress updates."
        )
    }
    return fallbacks.get(field, "Provide a concise, customer-focused statement.")


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_text(
    request: SuggestRequest,
    user: dict = Depends(get_current_user)
):
    """Lightweight text suggestion endpoint for form autofill."""
    allowed_fields = {"targetAudience", "problemSolved", "serviceType", "howItWorks"}
    if request.field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Unsupported suggestion field")

    context = request.context or {}
    suggestion_id = str(uuid.uuid4())
    market_profile = MarketDataService.get_market_profile(
        industry=_ctx(context, "industry", "general"),
        sub_industry=context.get("subIndustry"),
        service_type=context.get("serviceType"),
        delivery_model=_ctx(context, "deliveryModel", "service"),
        target_market=_ctx(context, "targetMarket", "unknown"),
        target_location=_ctx(context, "targetLocation", "global"),
    )
    macro_profile = await MacroDataService.get_macro_profile(_ctx(context, "targetLocation", "global"))
    issues = _derive_market_issues(context, market_profile, macro_profile)
    prompt = _build_suggestion_prompt(request.field, context, market_profile, macro_profile, issues)
    grounding_summary = (
        f"Issues considered: {'; '.join(issues)} "
        f"(market_source={market_profile.get('source')}, macro_source={macro_profile.get('source')})."
    )

    claude_key = os.environ.get("CLAUDE_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    emergent_key = os.environ.get("EMERGENT_LLM_KEY")
    api_key = claude_key or gemini_key or emergent_key
    if not api_key:
        return SuggestResponse(
            suggestion_id=suggestion_id,
            suggestion=_fallback_suggestion(request.field, context),
            provider="fallback",
            data_source="deterministic-market-context",
            grounding_summary=grounding_summary
        )

    try:
        suggestion = ""
        provider = "fallback"
        if claude_key or emergent_key or gemini_key:
            try:
                from emergentintegrations.llm.chat import LlmChat, UserMessage
                model_provider = "anthropic" if claude_key else ("google" if gemini_key else "openai")
                model_name = "claude-sonnet-4-20250514" if claude_key else ("gemini-2.0-flash" if gemini_key else "gpt-4o")
                chat = LlmChat(
                    api_key=api_key,
                    session_id=f"suggest_{suggestion_id}",
                    system_message="Return only the final suggested text with no extra formatting."
                ).with_model(model_provider, model_name)
                llm_response = await chat.send_message(UserMessage(content=prompt))
                suggestion = (getattr(llm_response, "content", "") or str(llm_response)).strip().splitlines()[0].strip()
                provider = "claude" if claude_key else ("gemini" if gemini_key else "openai")
            except Exception:
                suggestion = ""
        if (not suggestion) and gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.4, "max_output_tokens": 80}
            )
            suggestion = (getattr(response, "text", "") or "").strip().splitlines()[0].strip()
            provider = "gemini"
        if not suggestion:
            return SuggestResponse(
                suggestion_id=suggestion_id,
                suggestion=_fallback_suggestion(request.field, context),
                provider="fallback",
                data_source="deterministic-market-context",
                grounding_summary=grounding_summary
            )
        return SuggestResponse(
            suggestion_id=suggestion_id,
            suggestion=suggestion,
            provider=provider,
            data_source=f"market={market_profile.get('source')},macro={macro_profile.get('source')}",
            grounding_summary=grounding_summary
        )
    except Exception as e:
        err = str(e).lower()
        if "quota" in err or "429" in err or "resource_exhausted" in err:
            # Graceful fallback when quota is exhausted.
            return SuggestResponse(
                suggestion_id=suggestion_id,
                suggestion=_fallback_suggestion(request.field, context),
                provider="fallback",
                data_source="deterministic-market-context",
                grounding_summary=grounding_summary
            )
        logger.error(f"Suggestion error: {e}")
        return SuggestResponse(
            suggestion_id=suggestion_id,
            suggestion=_fallback_suggestion(request.field, context),
            provider="fallback",
            data_source="deterministic-market-context",
            grounding_summary=grounding_summary
        )


@router.post("/suggest-feedback")
async def submit_suggestion_feedback(
    request: SuggestFeedbackRequest,
    user: dict = Depends(get_current_user)
):
    """Store suggestion feedback for model quality improvement."""
    allowed_feedback = {"accept", "edit", "reject"}
    allowed_fields = {"targetAudience", "problemSolved", "serviceType", "howItWorks"}
    feedback = (request.feedback or "").strip().lower()
    if feedback not in allowed_feedback:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    if request.field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Unsupported field")

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "suggestion_id": request.suggestion_id,
        "user_id": user["id"],
        "field": request.field,
        "feedback": feedback,
        "suggested_text": request.suggested_text or "",
        "final_text": request.final_text or "",
        "provider": request.provider or "unknown",
        "context": request.context or {},
        "createdAt": now
    }
    await db.ai_suggestion_feedback.insert_one(doc)
    return {"message": "Feedback saved"}


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Send a message to the EnterprateAI AI Assistant.
    
    The assistant operates in three modes:
    - ADVISORY: General business guidance (default)
    - DATA_BACKED: Verified Companies House data
    - PRESENTATION: Structured output for stakeholders
    
    Modes are automatically detected based on the message content
    and any company identifiers provided.
    """
    try:
        user_id = user["id"]
        api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session_key = f"{user_id}_{session_id}"
        
        # Initialize session if new
        if session_key not in chat_sessions:
            chat_sessions[session_key] = {
                "history": [],
                "created_at": datetime.now(timezone.utc),
                "last_mode": AssistantMode.ADVISORY.value,
                "last_domain": EnterpateDomain.NAVIGATOR.value,
                "company_context": None
            }
        
        session = chat_sessions[session_key]
        
        # Store company context if provided
        if request.company_number or request.company_name:
            session["company_context"] = {
                "company_number": request.company_number,
                "company_name": request.company_name
            }
        
        # Process message through the assistant
        company_ctx = session.get("company_context") or {}
        result = await process_assistant_message(
            message=request.message,
            session_id=session_id,
            user_id=user_id,
            company_number=request.company_number or company_ctx.get("company_number"),
            company_name=request.company_name or company_ctx.get("company_name"),
            workspace_context=request.context
        )
        
        # Store in history
        session["history"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "company_number": request.company_number,
            "company_name": request.company_name
        })
        session["history"].append({
            "role": "assistant",
            "content": result.response,
            "timestamp": result.timestamp,
            "mode": result.mode,
            "domain": result.domain,
            "data_source": result.data_source,
            "confidence": result.confidence
        })
        
        # Update session state
        session["last_mode"] = result.mode
        session["last_domain"] = result.domain
        
        return ChatResponse(
            response=result.response,
            session_id=session_id,
            mode=result.mode,
            domain=result.domain,
            data_source=result.data_source,
            confidence=result.confidence,
            timestamp=result.timestamp
        )
        
    except ValueError as ve:
        logger.error(f"Chat configuration error: {str(ve)}")
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """Get chat history for a session with mode and domain metadata."""
    user_id = user["id"]
    session_key = f"{user_id}_{session_id}"
    
    if session_key not in chat_sessions:
        return {"history": [], "company_context": None}
    
    session = chat_sessions[session_key]
    return {
        "history": session["history"],
        "company_context": session.get("company_context"),
        "last_mode": session.get("last_mode"),
        "last_domain": session.get("last_domain")
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """Clear chat history and reset session state."""
    user_id = user["id"]
    session_key = f"{user_id}_{session_id}"
    
    if session_key in chat_sessions:
        del chat_sessions[session_key]
    
    return {"message": "Chat history cleared", "session_id": session_id}


@router.get("/modes")
async def get_assistant_modes(
    user: dict = Depends(get_current_user)
):
    """Get information about the assistant's operating modes."""
    return {
        "modes": [
            {
                "id": "advisory",
                "name": "Advisory Mode",
                "description": "General business guidance without company-specific data",
                "icon": "📋",
                "triggers": ["General questions", "Strategy advice", "Best practices"]
            },
            {
                "id": "data_backed",
                "name": "Data-Backed Mode",
                "description": "Verified intelligence from Companies House and other official sources",
                "icon": "✓",
                "triggers": ["Company verification", "Filing status", "Director lookups"]
            },
            {
                "id": "presentation",
                "name": "Presentation Mode",
                "description": "Structured output for investor, client, or board communication",
                "icon": "📊",
                "triggers": ["Summarise", "Create report", "Prepare presentation"]
            }
        ],
        "domains": [
            {
                "id": "genesis",
                "name": "Genesis AI",
                "description": "Idea discovery, validation, company formation, and business planning",
                "icon": "💡"
            },
            {
                "id": "navigator",
                "name": "Navigator AI",
                "description": "Operations, finance, compliance, and day-to-day business management",
                "icon": "🧭"
            },
            {
                "id": "growth",
                "name": "Growth AI",
                "description": "Marketing, lead generation, sales, and business expansion",
                "icon": "📈"
            }
        ]
    }


@router.post("/set-company-context")
async def set_company_context(
    session_id: str,
    company_number: Optional[str] = None,
    company_name: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Set company context for subsequent messages in the session."""
    user_id = user["id"]
    session_key = f"{user_id}_{session_id}"
    
    if session_key not in chat_sessions:
        chat_sessions[session_key] = {
            "history": [],
            "created_at": datetime.now(timezone.utc),
            "last_mode": AssistantMode.ADVISORY.value,
            "last_domain": EnterpateDomain.NAVIGATOR.value,
            "company_context": None
        }
    
    chat_sessions[session_key]["company_context"] = {
        "company_number": company_number,
        "company_name": company_name
    }
    
    return {
        "message": "Company context set",
        "company_context": chat_sessions[session_key]["company_context"]
    }
