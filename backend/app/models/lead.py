"""Lead model"""
from sqlalchemy import String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.schemas.enums import LeadStatus
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.workspace import Workspace

class Lead(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "leads"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus, name="lead_status"),
        default=LeadStatus.LEAD,
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="leads")
