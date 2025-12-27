"""
Chat routes for Enterprate OS AI Assistant

A decision-grade, verified, explainable business intelligence companion
that operates in three distinct modes: Advisory, Data-Backed, and Presentation.
"""
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.core.security import get_current_user
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


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Send a message to the Enterprate OS AI Assistant.
    
    The assistant operates in three modes:
    - ADVISORY: General business guidance (default)
    - DATA_BACKED: Verified Companies House data
    - PRESENTATION: Structured output for stakeholders
    
    Modes are automatically detected based on the message content
    and any company identifiers provided.
    """
    try:
        user_id = user["id"]
        api_key = os.environ.get("EMERGENT_LLM_KEY")
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
        result = await process_assistant_message(
            message=request.message,
            session_id=session_id,
            user_id=user_id,
            company_number=request.company_number or session.get("company_context", {}).get("company_number"),
            company_name=request.company_name or session.get("company_context", {}).get("company_name"),
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
