"""Project model"""
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.schemas.enums import ProjectType, ProjectStatus
from typing import Any, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.website import Website

class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    type: Mapped[ProjectType] = mapped_column(SQLEnum(ProjectType, name="project_type"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, name="project_status"),
        default=ProjectStatus.ACTIVE,
        nullable=False
    )
    # JSONB for flexible configuration data
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="projects")
    websites: Mapped[list["Website"]] = relationship(back_populates="project")
