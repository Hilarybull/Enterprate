"""Genesis AI schemas for Business/Product Idea Validation"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List, Any
from enum import Enum

class IdeaType(str, Enum):
    BUSINESS = "business"
    PRODUCT = "product"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TargetMarket(str, Enum):
    B2C = "B2C"
    B2B = "B2B"
    B2G = "B2G"
    OTHER = "Other"

class CustomerBudget(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"

class ValidationIdeaRequest(BaseModel):
    """Complete validation idea data model"""
    ideaType: str  # business | product
    ideaName: str
    ideaDescription: str
    industry: str
    subIndustry: Optional[str] = None
    problemSolved: str
    targetAudience: str
    urgencyLevel: str  # low | medium | high
    howItWorks: str
    deliveryModel: str
    targetMarket: str  # B2C | B2B | B2G | Other
    targetLocation: str
    customerBudget: str  # low | medium | high | unknown
    goToMarketChannel: List[str]  # SEO, Ads, Social, etc.

class ScoreBreakdown(BaseModel):
    """Individual score component"""
    name: str
    score: int
    maxScore: int
    assessment: str

class OutputCard(BaseModel):
    """UI output card"""
    title: str
    value: str
    description: Optional[str] = None
    status: Optional[str] = None  # positive, neutral, negative

class ValidationReport(BaseModel):
    """Complete validation report"""
    model_config = ConfigDict(extra="allow")
    
    # Core scores
    overallScore: int
    verdict: str  # PASS | PIVOT | KILL
    verdictReason: str
    
    # Score breakdown
    scoreBreakdown: List[ScoreBreakdown]
    
    # Output cards for UI
    outputCards: List[OutputCard]
    
    # Report sections
    strengths: List[str]
    weakAreas: List[str]
    keyRisks: List[str]
    recommendations: List[str]
    
    # Additional insights
    marketAssessment: Optional[str] = None
    competitiveLandscape: Optional[str] = None
    feasibilityNotes: Optional[str] = None
    
    # Next validation experiments
    nextExperiments: List[str]

class ValidationIdeaResponse(BaseModel):
    """Response from validation"""
    model_config = ConfigDict(extra="allow")
    
    id: str
    ideaType: str
    ideaName: str
    report: ValidationReport
    createdAt: str

# Legacy support
class IdeaScoreRequest(BaseModel):
    idea: str
    targetCustomer: Optional[str] = None

class IdeaScoreResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    score: int
    analysis: Dict[str, int]
    insights: List[str]
    nextSteps: List[str]
