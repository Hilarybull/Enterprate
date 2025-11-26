"""Chat routes for AI assistant"""
import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from app.core.security import get_current_user

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory chat sessions (for MVP - in production use Redis/DB)
chat_sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

SYSTEM_PROMPT = """You are the Enterprate OS AI Assistant - a helpful, professional AI guide for enterprise business management.

You help users with:
- **Idea Discovery & Validation**: Brainstorming business ideas, market research, competitive analysis
- **Website & Business Setup**: Creating business websites, branding guidance
- **Business Registration**: Company formation, legal requirements, compliance
- **Business Blueprint Generation**: Business plans, strategies, roadmaps
- **Finance Automation**: Invoicing, expense tracking, financial planning
- **Business Operations**: Process optimization, team management, workflows
- **Growth & Marketing**: Lead generation, sales strategies, marketing campaigns
- **Intelligence Graph**: Business analytics, insights, KPIs

Be concise, professional, and actionable. When users ask about features, guide them to the relevant module in the sidebar. Always be encouraging and supportive of their entrepreneurial journey.

Key features available:
- Genesis AI for idea validation
- Navigator for operations & invoicing
- Growth module for leads & marketing
- Website Builder for online presence
- Intelligence Graph for business insights"""

@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Send a message to the AI assistant and get a response"""
    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session_key = f"{user_id}_{session_id}"
        
        # Initialize or get existing chat
        if session_key not in chat_sessions:
            chat = LlmChat(
                api_key=api_key,
                session_id=session_key,
                system_message=SYSTEM_PROMPT
            ).with_model("openai", "gpt-4o")
            chat_sessions[session_key] = {
                "chat": chat,
                "history": [],
                "created_at": datetime.now(timezone.utc)
            }
        
        session = chat_sessions[session_key]
        chat = session["chat"]
        
        # Send message and get response
        user_message = UserMessage(text=request.message)
        response = await chat.send_message(user_message)
        
        # Store in history
        session["history"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        session["history"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return ChatResponse(response=response, session_id=session_id)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get chat history for a session"""
    session_key = f"{user_id}_{session_id}"
    
    if session_key not in chat_sessions:
        return {"history": []}
    
    return {"history": chat_sessions[session_key]["history"]}

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Clear chat history for a session"""
    session_key = f"{user_id}_{session_id}"
    
    if session_key in chat_sessions:
        del chat_sessions[session_key]
    
    return {"message": "Chat history cleared"}
