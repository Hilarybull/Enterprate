"""User model"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.workspace import WorkspaceMembership
    from app.models.intelligence import IntelligenceEvent

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    
    # Relationships
    workspace_memberships: Mapped[List["WorkspaceMembership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    intelligence_events: Mapped[List["IntelligenceEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
