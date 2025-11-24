"""Workspace-related schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid
from app.schemas.enums import UserRole, BusinessStatus

class Workspace(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    country: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    ownerId: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkspaceCreate(BaseModel):
    name: str
    country: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None

class WorkspaceMembership(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    workspaceId: str
    role: UserRole
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BusinessProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    businessName: Optional[str] = None
    status: BusinessStatus = BusinessStatus.IDEA
    brandTone: Optional[str] = None
    primaryGoal: Optional[str] = None
    targetAudience: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
