"""Intelligence event schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class EventCreate(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None

class EventResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    type: str
    data: Optional[Dict[str, Any]] = None
    occurredAt: Optional[str] = None
