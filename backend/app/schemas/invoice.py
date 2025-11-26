"""Invoice schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional

class InvoiceCreate(BaseModel):
    clientName: str
    clientEmail: str
    amount: float
    description: Optional[str] = None
    dueDate: Optional[str] = None

class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    clientName: str
    clientEmail: str
    amount: float
    status: Optional[str] = None
    invoiceNumber: Optional[str] = None
    description: Optional[str] = None
    dueDate: Optional[str] = None
