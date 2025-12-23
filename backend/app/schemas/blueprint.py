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
