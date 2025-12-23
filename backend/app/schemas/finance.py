"""Finance & Compliance schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum

class ExpenseCategory(str, Enum):
    OFFICE = "office"
    TRAVEL = "travel"
    MARKETING = "marketing"
    SOFTWARE = "software"
    UTILITIES = "utilities"
    PAYROLL = "payroll"
    EQUIPMENT = "equipment"
    PROFESSIONAL_SERVICES = "professional_services"
    OTHER = "other"

class ExpenseCreate(BaseModel):
    """Create expense"""
    description: str
    amount: float
    category: ExpenseCategory = ExpenseCategory.OTHER
    date: str
    vendor: Optional[str] = None
    receiptUrl: Optional[str] = None
    notes: Optional[str] = None

class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[ExpenseCategory] = None
    status: Optional[str] = None

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    description: str
    amount: float
    category: str
    date: str
    vendor: Optional[str] = None
    receiptUrl: Optional[str] = None
    notes: Optional[str] = None
    status: str = "pending"
    createdAt: str

class ReceiptScanRequest(BaseModel):
    """Receipt scan request with base64 image"""
    imageBase64: str
    filename: Optional[str] = None

class ReceiptScanResponse(BaseModel):
    """Extracted receipt data"""
    vendor: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    category: Optional[str] = None
    items: List[dict] = []
    confidence: float = 0.0
    rawText: Optional[str] = None

class TaxEstimateRequest(BaseModel):
    """Tax estimation request"""
    annualRevenue: float
    annualExpenses: float
    businessType: str = "sole_proprietor"  # sole_proprietor, llc, corporation
    country: str = "UK"

class TaxEstimateResponse(BaseModel):
    """Tax estimation response"""
    estimatedTax: float
    effectiveRate: float
    taxableIncome: float
    breakdown: List[dict] = []
    recommendations: List[str] = []

class ComplianceChecklistItem(BaseModel):
    """Single compliance item"""
    id: str
    title: str
    description: str
    category: str
    dueDate: Optional[str] = None
    completed: bool = False
    priority: str = "medium"  # low, medium, high

class ComplianceChecklistCreate(BaseModel):
    """Create compliance item"""
    title: str
    description: str
    category: str
    dueDate: Optional[str] = None
    priority: str = "medium"

class ComplianceChecklistUpdate(BaseModel):
    completed: Optional[bool] = None
    dueDate: Optional[str] = None
    priority: Optional[str] = None

class ComplianceChecklistResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    title: str
    description: str
    category: str
    dueDate: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    createdAt: str
