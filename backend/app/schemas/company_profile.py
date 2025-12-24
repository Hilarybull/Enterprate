"""Company Profile schemas - Single Source of Truth (SSOT)"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    # Companies House registered
    LTD = "ltd"  # Private Company Limited by Shares
    LTD_GUARANTEE = "ltd_guarantee"  # Private Company Limited by Guarantee
    PLC = "plc"  # Public Limited Company
    UNLIMITED = "unlimited"  # Unlimited Company
    LLP = "llp"  # Limited Liability Partnership
    LP = "lp"  # Limited Partnership
    CIC = "cic"  # Community Interest Company
    OVERSEAS = "overseas"  # Overseas Company (UK Establishment)
    ROYAL_CHARTER = "royal_charter"  # Royal Charter Company
    
    # NOT Companies House (clearly labeled)
    CIO = "cio"  # Charitable Incorporated Organisation (Charity Commission)
    COOP = "coop"  # Co-operative / Community Benefit Society (FCA)
    SOLE_TRADER = "sole_trader"  # Sole Trader (HMRC only)
    PARTNERSHIP = "partnership"  # General Partnership


class RegistrationAuthority(str, Enum):
    COMPANIES_HOUSE = "companies_house"
    CHARITY_COMMISSION = "charity_commission"
    FCA = "fca"
    PRIVY_COUNCIL = "privy_council"
    HMRC = "hmrc"
    NONE = "none"


class EntityTypeInfo(BaseModel):
    """Complete entity type information"""
    id: str
    title: str
    shortName: str
    description: str
    useCases: List[str] = []
    registrationAuthority: str
    authorityLabel: str
    isCompaniesHouse: bool = True
    constraints: List[str] = []
    currentFee: Optional[str] = None
    futureFee: Optional[str] = None  # Fee from 1 Feb 2026
    feeNote: Optional[str] = None


class CompaniesHouseFees(BaseModel):
    """Companies House fee structure - date-aware"""
    model_config = ConfigDict(extra="allow")
    entityType: str
    currentFee: str
    futureFee: str  # From 1 Feb 2026
    effectiveFrom: str = "2024-05-01"
    futureEffectiveFrom: str = "2026-02-01"
    source: str = "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees"
    lastUpdated: str


class OfficialProfile(BaseModel):
    """Companies House fetched data - READ-ONLY"""
    model_config = ConfigDict(extra="allow")
    companyNumber: Optional[str] = None
    companyName: Optional[str] = None
    companyStatus: Optional[str] = None
    companyType: Optional[str] = None
    incorporationDate: Optional[str] = None
    sicCodes: List[str] = []
    registeredOffice: Optional[Dict[str, Any]] = None
    officers: List[Dict[str, Any]] = []
    confirmationStatementDue: Optional[str] = None
    accountsDue: Optional[str] = None
    lastRefreshed: Optional[str] = None


class OperatingProfile(BaseModel):
    """User-editable operating details"""
    model_config = ConfigDict(extra="allow")
    tradingName: Optional[str] = None
    tradingAddress: Optional[str] = None
    marketingDescription: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    socialMedia: Dict[str, str] = {}
    industry: Optional[str] = None


class DerivedProfile(BaseModel):
    """AI-generated brand elements"""
    model_config = ConfigDict(extra="allow")
    tagline: Optional[str] = None
    elevatorPitch: Optional[str] = None
    tone: Optional[str] = None  # professional, friendly, premium
    keywords: List[str] = []
    brandColors: List[str] = []
    fontPairings: List[Dict[str, str]] = []
    visualDirection: Optional[str] = None  # modern, corporate, playful, minimal, luxury
    generatedAt: Optional[str] = None


class CompanyProfileCreate(BaseModel):
    """Create company profile"""
    entityType: Optional[str] = None
    proposedName: Optional[str] = None
    businessDescription: Optional[str] = None
    selectedSicCodes: List[str] = []
    targetMarket: Optional[str] = None
    fundingGoal: Optional[float] = None


class CompanyProfileUpdate(BaseModel):
    """Update company profile"""
    operatingProfile: Optional[OperatingProfile] = None
    derivedProfile: Optional[DerivedProfile] = None
    registrationData: Optional[Dict[str, Any]] = None


class CompanyProfileResponse(BaseModel):
    """Full company profile response"""
    model_config = ConfigDict(extra="allow")
    id: str
    workspaceId: str
    
    # Registration status
    entityType: Optional[str] = None
    isRegistrationConfirmed: bool = False
    
    # Name checking
    proposedName: Optional[str] = None
    legalNameConfirmed: bool = False
    legalName: Optional[str] = None
    nameCheckedAt: Optional[str] = None
    nameCheckResults: Optional[Dict[str, Any]] = None
    
    # Business details
    businessDescription: Optional[str] = None
    selectedSicCodes: List[str] = []
    targetMarket: Optional[str] = None
    fundingGoal: Optional[float] = None
    
    # Registration wizard data
    registrationData: Optional[Dict[str, Any]] = None
    
    # Three profiles
    officialProfile: Optional[OfficialProfile] = None
    operatingProfile: Optional[OperatingProfile] = None
    derivedProfile: Optional[DerivedProfile] = None
    
    createdAt: str
    updatedAt: Optional[str] = None


# Companies House API schemas
class NameSearchRequest(BaseModel):
    """Name availability search request"""
    companyName: str
    includeDisqualified: bool = False


class NameSuggestion(BaseModel):
    """AI-generated name suggestion"""
    name: str
    reason: str
    type: str  # descriptor, abbreviation, stem, variation


class NameSearchResult(BaseModel):
    """Name search result"""
    model_config = ConfigDict(extra="allow")
    searchedName: str
    isAvailable: bool
    confidence: float  # 0-1
    exactMatches: List[Dict[str, Any]] = []
    similarMatches: List[Dict[str, Any]] = []
    suggestions: List[NameSuggestion] = []
    checkedAt: str


class RegistrationConfirmRequest(BaseModel):
    """Post-registration confirmation request"""
    companyNumber: str
    postcode: Optional[str] = None  # For verification


class RegistrationConfirmResponse(BaseModel):
    """Confirmed registration details from Companies House"""
    model_config = ConfigDict(extra="allow")
    success: bool
    message: str
    companyData: Optional[Dict[str, Any]] = None
