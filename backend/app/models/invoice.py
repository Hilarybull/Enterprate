"""Invoice model"""
from sqlalchemy import String, ForeignKey, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base, UUIDMixin, TimestampMixin
from app.schemas.enums import InvoiceStatus
from typing import Any, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from app.models.workspace import Workspace

class Invoice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invoices"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, name="invoice_status"),
        default=InvoiceStatus.DRAFT,
        nullable=False
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # JSONB for flexible invoice items
    items: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="invoices")
