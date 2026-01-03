"""Growth Agent schemas"""
from typing import List, Optional, Any
from pydantic import BaseModel
from datetime import datetime


class GrowthAlert(BaseModel):
    """Growth alert schema"""
    id: str
    type: str
    severity: str  # critical, warning, info
    title: str
    message: str
    suggestedAction: Optional[str] = None
    actionLabel: Optional[str] = None


class LeadsAnalysis(BaseModel):
    """Lead analysis schema"""
    currentPeriod: int
    previousPeriod: int
    percentChange: float
    conversionRate: float
    conversionChange: float
    trend: str  # up, down, stable


class RevenueAnalysis(BaseModel):
    """Revenue analysis schema"""
    currentRevenue: float
    previousRevenue: float
    percentChange: float
    invoiceCount: int
    paidInvoices: int
    trend: str


class CampaignAnalysis(BaseModel):
    """Campaign analysis schema"""
    activeCampaigns: int
    totalCampaigns: int
    totalBudget: float
    totalConversions: int
    totalClicks: int
    averageCTR: float
    trend: str


class PerformanceAnalysisResponse(BaseModel):
    """Business performance analysis response"""
    analysisDate: str
    healthScore: int
    leads: LeadsAnalysis
    revenue: RevenueAnalysis
    campaigns: CampaignAnalysis
    alerts: List[GrowthAlert]
    status: str  # healthy, warning, critical


class GrowthAction(BaseModel):
    """Individual growth action"""
    type: str
    platform: Optional[str] = None
    content: Optional[str] = None
    schedule: Optional[str] = None
    target: Optional[str] = None
    template: Optional[str] = None
    discount: Optional[str] = None
    duration: Optional[str] = None
    content_type: Optional[str] = None
    frequency: Optional[str] = None


class GrowthRecommendation(BaseModel):
    """Growth recommendation schema"""
    id: str
    title: str
    type: str
    description: str
    actions: List[GrowthAction]
    expectedOutcome: str
    estimatedBudget: float
    duration: str
    status: str  # pending, approved, rejected


class GenerateRecommendationRequest(BaseModel):
    """Request to generate growth recommendation"""
    alertType: str
    alertId: Optional[str] = None


class ApproveRecommendationRequest(BaseModel):
    """Request to approve recommendation"""
    recommendationId: str


class RejectRecommendationRequest(BaseModel):
    """Request to reject recommendation"""
    recommendationId: str
    reason: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response after processing recommendation"""
    id: str
    status: str
    executedActions: Optional[List[dict]] = None
    message: str
