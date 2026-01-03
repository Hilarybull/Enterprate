"""Dynamic fees configuration schemas"""
from typing import List, Optional
from pydantic import BaseModel


class RegistrationFee(BaseModel):
    """Single registration fee entry"""
    id: str
    businessType: str
    title: str
    registrationAuthority: str
    onlineFee: str
    paperFee: Optional[str] = None
    sameDayFee: Optional[str] = None
    notes: Optional[str] = None
    sourceUrl: str
    lastUpdated: str


class FeesConfigResponse(BaseModel):
    """Response with all fees configuration"""
    fees: List[RegistrationFee]
    lastUpdated: str
    source: str
