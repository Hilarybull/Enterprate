"""Website-related schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid

class Website(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    projectId: Optional[str] = None
    name: str
    domain: Optional[str] = None
    published: bool = False
    config: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WebsiteCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class WebsitePage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    websiteId: str
    path: str
    title: str
    content: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WebsitePageCreate(BaseModel):
    path: str
    title: str
    content: Optional[Dict[str, Any]] = None
