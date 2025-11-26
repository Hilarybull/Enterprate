"""Lead schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional

class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str = "WEBSITE"
    status: Optional[str] = "NEW"

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    name: Optional[str] = None

class LeadResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
