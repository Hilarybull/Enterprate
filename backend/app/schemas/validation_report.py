"""Comprehensive Idea Validation Report schemas (IdeaBrowser-style)"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime


class ReportStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ScoreItem(BaseModel):
    """Individual score with value and label"""
    value: int = Field(ge=0, le=10)
    label: str
    description: Optional[str] = None


class AIScores(BaseModel):
    """Main AI scoring cards"""
    opportunity: ScoreItem
    problem: ScoreItem
    feasibility: ScoreItem
    whyNow: ScoreItem


class BusinessFitItem(BaseModel):
    """Business fit metric"""
    indicator: Optional[str] = None  # e.g., "$$$"
    score: Optional[int] = None  # e.g., 8/10
    description: str


class BusinessFit(BaseModel):
    """Business fit section"""
    revenuePotential: BusinessFitItem
    executionDifficulty: BusinessFitItem
    goToMarket: BusinessFitItem
    rightForYou: Optional[str] = None


class OfferTier(BaseModel):
    """Value ladder tier"""
    tier: str  # e.g., "LEAD MAGNET", "FRONTEND", "CORE"
    name: str
    price: str  # e.g., "Free", "$15/month"
    description: str


class FrameworkScore(BaseModel):
    """Framework analysis score"""
    name: str
    score: int
    maxScore: int = 10
    visual: Optional[str] = None  # "gauge", "bar", "matrix"


class FrameworkAnalysis(BaseModel):
    """Individual framework analysis"""
    name: str
    description: Optional[str] = None
    scores: Optional[List[FrameworkScore]] = None
    overallScore: Optional[int] = None


class CommunitySignal(BaseModel):
    """Community platform signal"""
    platform: str
    details: str  # e.g., "5 subreddits - 2.5M+ members"
    score: int  # 0-10


class KeywordData(BaseModel):
    """Keyword analysis data"""
    keyword: str
    volume: str  # e.g., "5.4K"
    competition: Optional[str] = None  # "LOW", "MEDIUM", "HIGH"
    growth: Optional[str] = None  # e.g., "+4809%"


class Categorization(BaseModel):
    """Idea categorization"""
    type: str  # e.g., "SaaS"
    market: str  # e.g., "B2C"
    target: Optional[str] = None
    mainCompetitor: Optional[str] = None
    trendAnalysis: Optional[str] = None


class ComprehensiveReport(BaseModel):
    """Full IdeaBrowser-style validation report"""
    model_config = ConfigDict(extra="allow")
    
    # Header section
    title: str
    tags: List[str]  # e.g., ["Perfect Timing", "Massive Market"]
    
    # Main description
    description: str
    disclaimer: Optional[str] = None
    
    # AI Scores (right column top)
    scores: AIScores
    
    # Business Fit (right column)
    businessFit: BusinessFit
    
    # Value Ladder / Offer section
    offer: List[OfferTier]
    
    # Content sections
    whyNow: str
    proofSignals: str
    marketGap: str
    executionPlan: str
    
    # Framework Analysis
    frameworkFit: List[FrameworkAnalysis]
    
    # Categorization
    categorization: Categorization
    
    # Community signals
    communitySignals: List[CommunitySignal]
    
    # Keywords
    topKeywords: List[KeywordData]
    
    # Trend data
    trendKeyword: Optional[str] = None
    trendVolume: Optional[str] = None
    trendGrowth: Optional[str] = None
    
    # Pre-built prompts for "Start Building"
    buildPrompts: Optional[List[str]] = None
    
    # Q&A suggestions
    suggestedQuestions: Optional[List[str]] = None


class ValidationReportCreate(BaseModel):
    """Request to create a validation report"""
    ideaType: Optional[str] = None
    ideaName: Optional[str] = None
    ideaDescription: Optional[str] = None
    industry: Optional[str] = None
    subIndustry: Optional[str] = None
    problemSolved: Optional[str] = None
    targetAudience: Optional[str] = None
    urgencyLevel: Optional[str] = None
    howItWorks: Optional[str] = None
    deliveryModel: Optional[str] = None
    targetMarket: Optional[str] = None
    targetLocation: Optional[str] = None
    customerBudget: Optional[str] = None
    goToMarketChannel: List[str] = Field(default_factory=list)
    
    # Business idea validation journey fields
    businessType: Optional[str] = None  # service_micro_business, agency, etc.
    founderAvailabilityHoursPerWeek: Optional[int] = Field(default=None, ge=0)
    stage: Optional[str] = "idea"
    customerSegment: Optional[str] = None
    customerSegmentNotes: Optional[str] = None
    problemType: Optional[List[str]] = Field(default_factory=list)  # cost | time | compliance | quality | reliability (multi-select)
    problemFrequency: Optional[str] = None  # daily | weekly | monthly
    currentAlternatives: Optional[str] = None
    serviceType: Optional[str] = None
    packageTiers: Optional[str] = None
    upfrontCosts: Optional[float] = Field(default=None, ge=0)
    
    # Deterministic modeling inputs (Validate My Idea v1)
    pricingModel: Optional[str] = None  # hourly | fixed_job | retainer | subscription
    priceAmount: Optional[float] = Field(default=None, ge=0)
    deliverableUnit: Optional[str] = None  # hours | job | month
    expectedUnitsPerMonth: Optional[int] = Field(default=None, ge=0)
    expectedCustomers: Optional[int] = Field(default=None, ge=0)
    salesCycleDays: Optional[int] = Field(default=None, ge=0)
    paymentTermsDays: Optional[int] = Field(default=None, ge=0)
    variableCostPerUnit: Optional[float] = Field(default=None, ge=0)
    fixedMonthlyCosts: Optional[float] = Field(default=None, ge=0)
    founderDrawMonthly: Optional[float] = Field(default=None, ge=0)
    contractorCostsMonthly: Optional[float] = Field(default=None, ge=0)
    staffCount: Optional[int] = Field(default=None, ge=0)
    capacityPerStaffPerMonth: Optional[float] = Field(default=None, ge=0)
    cashBuffer: Optional[float] = Field(default=None, ge=0)


class ValidationReportDB(BaseModel):
    """Full validation report as stored in database"""
    model_config = ConfigDict(extra="allow")
    
    id: str
    workspace_id: str
    user_id: str
    status: ReportStatus = ReportStatus.PENDING
    
    # Original input data
    ideaInput: ValidationReportCreate
    
    # Generated report
    report: ComprehensiveReport
    
    # Timestamps
    createdAt: str
    updatedAt: Optional[str] = None


class ValidationReportResponse(BaseModel):
    """Response for a single report"""
    model_config = ConfigDict(extra="allow")
    
    id: str
    status: str
    ideaInput: ValidationReportCreate
    report: ComprehensiveReport
    createdAt: str
    updatedAt: Optional[str] = None


class ValidationReportListItem(BaseModel):
    """List item for report history"""
    id: str
    ideaName: str
    ideaType: str
    status: str
    overallScore: int  # Derived from opportunity score
    verdict: str  # PASS/PIVOT/KILL based on score
    createdAt: str


class ReportStatusUpdate(BaseModel):
    """Update report status"""
    status: ReportStatus


class EngagementStats(BaseModel):
    """User engagement statistics"""
    totalValidations: int
    acceptedCount: int
    rejectedCount: int
    pendingCount: int
    ideaValidationStatus: str = "in_progress"  # in_progress | finished
    ideaValidationProgress: int = 0
