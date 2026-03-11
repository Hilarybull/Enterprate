"""Business Blueprint schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum

class BlueprintSectionType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    MARKET_ANALYSIS = "market_analysis"
    PRODUCTS_SERVICES = "products_services"
    MARKETING_STRATEGY = "marketing_strategy"
    OPERATIONS_PLAN = "operations_plan"
    FINANCIAL_PROJECTIONS = "financial_projections"
    SWOT_ANALYSIS = "swot_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"

class BlueprintDocumentType(str, Enum):
    BUSINESS_PLAN = "business_plan"
    CLIENT_PROPOSAL = "client_proposal"
    SALES_LETTER = "sales_letter"
    SALES_QUOTATION = "sales_quotation"
    CASHFLOW_ANALYSIS = "cashflow_analysis"
    FINANCIAL_PROJECTION = "financial_projection"

class BlueprintCreate(BaseModel):
    """Create a new business blueprint"""
    businessName: str
    industry: str
    description: str
    targetMarket: Optional[str] = None
    businessModel: Optional[str] = None
    fundingGoal: Optional[float] = None

class BlueprintSectionGenerate(BaseModel):
    """Generate a specific section"""
    blueprintId: str
    sectionType: BlueprintSectionType

class BlueprintUpdate(BaseModel):
    """Update blueprint"""
    businessName: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class SWOTAnalysis(BaseModel):
    """SWOT Analysis structure"""
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

class FinancialProjection(BaseModel):
    """Financial projection item"""
    year: int
    revenue: float
    expenses: float
    netIncome: float
    growthRate: Optional[float] = None

class BlueprintSectionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    sectionType: str
    title: str
    content: str
    generatedAt: str

class BlueprintResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    businessName: str
    industry: str
    description: str
    targetMarket: Optional[str] = None
    businessModel: Optional[str] = None
    fundingGoal: Optional[float] = None
    status: str = "draft"
    sections: List[BlueprintSectionResponse] = []
    swotAnalysis: Optional[SWOTAnalysis] = None
    financialProjections: List[FinancialProjection] = []
    createdAt: str
    updatedAt: Optional[str] = None


class BlueprintRequirement(BaseModel):
    key: str
    label: str
    source: str


class BlueprintEligibilityItem(BaseModel):
    documentType: BlueprintDocumentType
    label: str
    ready: bool
    missingFields: List[BlueprintRequirement] = []
    completionPercent: int = 0


class BlueprintEligibilityResponse(BaseModel):
    businessId: str
    available: List[BlueprintEligibilityItem] = []
    partial: List[BlueprintEligibilityItem] = []
    missing: List[BlueprintEligibilityItem] = []


class BlueprintInputRequest(BaseModel):
    businessId: Optional[str] = None
    documentType: BlueprintDocumentType
    inputs: dict
    provenance: Optional[dict] = None


class BlueprintGenerateRequest(BaseModel):
    businessId: Optional[str] = None
    documentType: BlueprintDocumentType
    regenerate: bool = False


class BlueprintSectionUpdateRequest(BaseModel):
    sectionId: str
    content: str


class BlueprintSectionRegenerateRequest(BaseModel):
    sectionId: str


class BlueprintDocumentSection(BaseModel):
    id: str
    title: str
    content: str
    editable: bool = True


class BlueprintDocumentVersion(BaseModel):
    version: int
    createdAt: str
    sourceStateVersion: str
    templateVersion: str
    llmGenerationVersion: str


class BlueprintDocumentResponse(BaseModel):
    id: str
    workspaceId: str
    businessId: str
    documentType: BlueprintDocumentType
    title: str
    status: str
    renderedHtml: str
    sections: List[BlueprintDocumentSection] = []
    sourceStateVersion: str
    templateVersion: str
    llmGenerationVersion: str
    versions: List[BlueprintDocumentVersion] = []
    createdBy: str
    createdAt: str
    updatedAt: str
