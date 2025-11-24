"""Intelligence event model"""
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base, UUIDMixin
from typing import Any, TYPE_CHECKING
from datetime import datetime, timezone
import uuid

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.user import User

class IntelligenceEvent(Base, UUIDMixin):
    __tablename__ = "intelligence_events"
    
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # JSONB for flexible event payload
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="intelligence_events")
    user: Mapped["User"] = relationship(back_populates="intelligence_events")
