"""Marketing/Growth schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class CampaignType(str, Enum):
    EMAIL = "email"
    SOCIAL = "social"
    CONTENT = "content"
    PPC = "ppc"
    EVENT = "event"
    OTHER = "other"

class CampaignCreate(BaseModel):
    """Create marketing campaign"""
    name: str
    description: Optional[str] = None
    type: CampaignType = CampaignType.OTHER
    budget: Optional[float] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    targetAudience: Optional[str] = None
    goals: List[str] = []
    channels: List[str] = []

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    budget: Optional[float] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class CampaignMetrics(BaseModel):
    """Campaign performance metrics"""
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    ctr: float = 0.0  # Click-through rate
    cpc: float = 0.0  # Cost per click
    roi: float = 0.0  # Return on investment

class CampaignResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    description: Optional[str] = None
    type: str
    status: str = "draft"
    budget: Optional[float] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    targetAudience: Optional[str] = None
    goals: List[str] = []
    channels: List[str] = []
    metrics: Optional[CampaignMetrics] = None
    createdAt: str

# Social Media
class SocialPostCreate(BaseModel):
    """Create social media post suggestion"""
    platform: str  # twitter, linkedin, facebook, instagram
    content: str
    scheduledFor: Optional[str] = None
    campaignId: Optional[str] = None
    mediaUrls: List[str] = []
    hashtags: List[str] = []

class SocialPostUpdate(BaseModel):
    content: Optional[str] = None
    scheduledFor: Optional[str] = None
    status: Optional[str] = None

class SocialPostResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    platform: str
    content: str
    status: str = "draft"  # draft, scheduled, posted
    scheduledFor: Optional[str] = None
    postedAt: Optional[str] = None
    campaignId: Optional[str] = None
    mediaUrls: List[str] = []
    hashtags: List[str] = []
    createdAt: str

class SocialPostGenerateRequest(BaseModel):
    """AI-generate social post"""
    platform: str
    topic: str
    tone: str = "professional"  # professional, casual, humorous, inspiring
    includeEmojis: bool = True
    includeHashtags: bool = True
    campaignId: Optional[str] = None

# Analytics
class AnalyticsPeriod(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AnalyticsRequest(BaseModel):
    """Request analytics data"""
    period: AnalyticsPeriod = AnalyticsPeriod.MONTH
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class LeadAnalytics(BaseModel):
    """Lead analytics"""
    totalLeads: int = 0
    newLeads: int = 0
    convertedLeads: int = 0
    conversionRate: float = 0.0
    leadsBySource: dict = {}
    leadsByStatus: dict = {}
    trend: List[dict] = []  # [{date, count}]

class CampaignAnalytics(BaseModel):
    """Campaign analytics"""
    totalCampaigns: int = 0
    activeCampaigns: int = 0
    totalBudget: float = 0.0
    totalSpend: float = 0.0
    avgROI: float = 0.0
    topPerforming: List[dict] = []

class GrowthAnalyticsResponse(BaseModel):
    """Combined growth analytics"""
    period: str
    leads: LeadAnalytics
    campaigns: CampaignAnalytics
    summary: dict = {}
