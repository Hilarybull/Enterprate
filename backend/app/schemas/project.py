"""Project-related schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from app.schemas.enums import ProjectType, ProjectStatus

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    type: ProjectType
    name: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    config: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    type: ProjectType
    name: str
    config: Optional[Dict[str, Any]] = None
