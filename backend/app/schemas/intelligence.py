"""Intelligence event schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid

class IntelligenceEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    userId: Optional[str] = None
    type: str
    payload: Optional[Dict[str, Any]] = None
    occurredAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IntelligenceEventCreate(BaseModel):
    type: str
    payload: Optional[Dict[str, Any]] = None
