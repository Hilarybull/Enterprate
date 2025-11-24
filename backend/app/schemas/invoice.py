"""Invoice-related schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from app.schemas.enums import InvoiceStatus

class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str
    customerName: str
    amount: float
    currency: str = "USD"
    status: InvoiceStatus = InvoiceStatus.DRAFT
    dueDate: Optional[datetime] = None
    items: Optional[List[Dict[str, Any]]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvoiceCreate(BaseModel):
    customerName: str
    amount: float
    currency: str = "USD"
    dueDate: Optional[datetime] = None
    items: Optional[List[Dict[str, Any]]] = None

class InvoiceUpdate(BaseModel):
    customerName: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[InvoiceStatus] = None
    dueDate: Optional[datetime] = None
