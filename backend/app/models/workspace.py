"""Workspace-related models"""
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.schemas.enums import UserRole, BusinessStatus
from typing import List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.website import Website
    from app.models.invoice import Invoice
    from app.models.lead import Lead
    from app.models.intelligence import IntelligenceEvent

class Workspace(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspaces"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    memberships: Mapped[List["WorkspaceMembership"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    business_profile: Mapped["BusinessProfile"] = relationship(
        back_populates="workspace",
        uselist=False,
        cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    websites: Mapped[List["Website"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    leads: Mapped[List["Lead"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    intelligence_events: Mapped[List["IntelligenceEvent"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan"
    )

class WorkspaceMembership(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspace_memberships"
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="user_role"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")
    workspace: Mapped["Workspace"] = relationship(back_populates="memberships")

class BusinessProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "business_profiles"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        unique=True,
        nullable=False
    )
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[BusinessStatus] = mapped_column(
        SQLEnum(BusinessStatus, name="business_status"),
        default=BusinessStatus.IDEA,
        nullable=False
    )
    brand_tone: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_goal: Mapped[str | None] = mapped_column(String(500), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="business_profile")
