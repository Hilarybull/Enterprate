"""Website models"""
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base, UUIDMixin, TimestampMixin
from typing import Any, List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.project import Project

class Website(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "websites"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # JSONB for flexible website configuration
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="websites")
    project: Mapped["Project"] = relationship(back_populates="websites")
    pages: Mapped[List["WebsitePage"]] = relationship(
        back_populates="website",
        cascade="all, delete-orphan"
    )

class WebsitePage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "website_pages"
    
    website_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # JSONB for flexible page content (sections, blocks, etc.)
    content: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    website: Mapped["Website"] = relationship(back_populates="pages")
