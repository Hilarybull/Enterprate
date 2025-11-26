"""Website schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional

class WebsiteCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[str] = None

class WebsiteResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    domain: Optional[str] = None
    status: Optional[str] = None
