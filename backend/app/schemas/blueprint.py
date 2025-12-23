"""Comprehensive Business Blueprint schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BlueprintType(str, Enum):
    BUSINESS_PLAN = "business_plan"
    FINANCIAL_PROJECTION = "financial_projection"
    PRICING_MODEL = "pricing_model"
    OPERATIONAL_MODEL = "operational_model"
    GTM_STRATEGY = "gtm_strategy"
    CASHFLOW_FORECAST = "cashflow_forecast"


class BlueprintStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# Business Plan
class BusinessPlanInput(BaseModel):
    businessName: str
    industry: str
    businessDescription: str
    targetMarket: str
    products: Optional[str] = None
    competitiveAdvantage: Optional[str] = None
    revenueModel: Optional[str] = None
    fundingNeeds: Optional[str] = None


class BusinessPlanSection(BaseModel):
    title: str
    content: str
    order: int


class BusinessPlanOutput(BaseModel):
    executiveSummary: str
    companyDescription: str
    marketAnalysis: str
    organization: str
    productsServices: str
    marketingStrategy: str
    operationalPlan: str
    financialPlan: str
    appendix: Optional[str] = None


# Financial Projection
class FinancialProjectionInput(BaseModel):
    businessName: str
    industry: str
    startingCapital: float
    monthlyRevenue: float
    monthlyExpenses: float
    growthRate: float = 10.0
    employeeCount: int = 1
    additionalNotes: Optional[str] = None


class MonthlyProjection(BaseModel):
    month: int
    revenue: float
    expenses: float
    profit: float
    cumulativeProfit: float


class FinancialProjectionOutput(BaseModel):
    summary: str
    projections: List[MonthlyProjection]
    breakEvenMonth: Optional[int] = None
    totalRevenue: float
    totalExpenses: float
    netProfit: float
    profitMargin: float
    keyAssumptions: List[str]
    recommendations: List[str]


# Pricing Model
class PricingModelInput(BaseModel):
    businessName: str
    productService: str
    targetMarket: str
    costPerUnit: float
    competitorPrices: Optional[str] = None
    valueProposition: Optional[str] = None
    pricingGoal: str = "profit_maximization"  # profit_maximization, market_penetration, premium


class PricingTier(BaseModel):
    name: str
    price: str
    features: List[str]
    targetCustomer: str
    recommended: bool = False


class PricingModelOutput(BaseModel):
    strategy: str
    recommendedPrice: float
    priceRange: Dict[str, float]
    tiers: List[PricingTier]
    justification: str
    competitiveAnalysis: str
    recommendations: List[str]


# Operational Model
class OperationalModelInput(BaseModel):
    businessName: str
    industry: str
    businessModel: str  # saas, service, product, marketplace
    teamSize: int
    location: str
    keyActivities: Optional[str] = None


class ProcessStep(BaseModel):
    name: str
    description: str
    responsible: str
    tools: List[str]
    frequency: str


class OperationalModelOutput(BaseModel):
    summary: str
    keyProcesses: List[ProcessStep]
    resourceRequirements: Dict[str, Any]
    technologyStack: List[str]
    keyMetrics: List[str]
    scalabilityPlan: str
    riskMitigation: List[str]


# Go-To-Market Strategy
class GTMStrategyInput(BaseModel):
    businessName: str
    productService: str
    targetMarket: str
    uniqueValue: str
    budget: float
    timeline: str = "6_months"
    channels: Optional[List[str]] = None


class MarketingChannel(BaseModel):
    name: str
    strategy: str
    budget: float
    expectedROI: str
    timeline: str
    kpis: List[str]


class GTMStrategyOutput(BaseModel):
    summary: str
    targetAudience: Dict[str, Any]
    positioning: str
    channels: List[MarketingChannel]
    launchPlan: List[Dict[str, str]]
    budgetAllocation: Dict[str, float]
    milestones: List[Dict[str, str]]
    successMetrics: List[str]


# Cashflow Forecast
class CashflowForecastInput(BaseModel):
    businessName: str
    startingCash: float
    monthlyIncome: float
    monthlyExpenses: float
    oneTimeExpenses: Optional[List[Dict[str, Any]]] = None
    expectedPaymentTerms: int = 30  # days


class CashflowMonth(BaseModel):
    month: int
    inflows: float
    outflows: float
    netCashflow: float
    closingBalance: float


class CashflowForecastOutput(BaseModel):
    summary: str
    forecast: List[CashflowMonth]
    lowestPoint: Dict[str, Any]
    averageMonthlyBalance: float
    warnings: List[str]
    recommendations: List[str]


# Blueprint Document (stored in DB)
class BlueprintDocument(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    type: BlueprintType
    status: BlueprintStatus
    title: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    createdAt: str
    updatedAt: Optional[str] = None


class BlueprintListItem(BaseModel):
    id: str
    type: str
    title: str
    status: str
    createdAt: str
