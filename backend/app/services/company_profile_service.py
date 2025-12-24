"""Company Profile Service - Central SSOT for company data"""
import uuid
import os
import httpx
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.company_profile import (
    CompanyProfileCreate, CompanyProfileUpdate, OfficialProfile,
    OperatingProfile, DerivedProfile, EntityTypeInfo, CompaniesHouseFees,
    NameSearchRequest, NameSearchResult, NameSuggestion,
    RegistrationConfirmRequest
)

# Try to import LLM integration for name suggestions
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


# Companies House API configuration
CH_API_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
CH_API_BASE = "https://api.company-information.service.gov.uk"


class CompanyProfileService:
    """Service for managing company profiles - Single Source of Truth"""
    
    # Entity types with complete information
    ENTITY_TYPES: List[EntityTypeInfo] = [
        # Companies House registered
        EntityTypeInfo(
            id="ltd",
            title="Private Company Limited by Shares (Ltd)",
            shortName="Ltd",
            description="Most common company type. Shareholders' liability is limited to their investment. Separate legal entity from its owners.",
            useCases=["Small to medium businesses", "Startups seeking investment", "Freelancers wanting credibility", "Family businesses"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["Must file annual accounts", "Must file confirmation statement", "Minimum 1 director, 1 shareholder"],
            currentFee="£50 (online) / £71 (paper)",
            futureFee="£50 (online) / £78 (paper)",
            feeNote="Standard registration. Same day: £78 online."
        ),
        EntityTypeInfo(
            id="ltd_guarantee",
            title="Private Company Limited by Guarantee",
            shortName="Ltd by Guarantee",
            description="Members guarantee to pay a fixed amount if company is wound up. No share capital. Often used by non-profits.",
            useCases=["Non-profit organisations", "Membership organisations", "Clubs and societies", "Trade associations"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["No share capital", "Members liable up to guaranteed amount", "Cannot distribute profits to members"],
            currentFee="£50 (online) / £71 (paper)",
            futureFee="£50 (online) / £78 (paper)"
        ),
        EntityTypeInfo(
            id="plc",
            title="Public Limited Company (PLC)",
            shortName="PLC",
            description="Can offer shares to the public. Required for listing on stock exchange. Higher compliance requirements.",
            useCases=["Large businesses", "Companies planning IPO", "Businesses seeking public investment"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["Minimum £50,000 share capital", "At least 25% must be paid up", "Minimum 2 directors", "Must have company secretary", "Higher audit requirements"],
            currentFee="£50 (online) / £71 (paper)",
            futureFee="£50 (online) / £78 (paper)"
        ),
        EntityTypeInfo(
            id="unlimited",
            title="Unlimited Company",
            shortName="Unlimited",
            description="Members have unlimited liability for company debts. Rare structure with some privacy advantages.",
            useCases=["Professional practices", "Private equity structures", "Family investment vehicles"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["Unlimited personal liability", "Less common structure", "May not need to file accounts publicly"],
            currentFee="£50 (online) / £71 (paper)",
            futureFee="£50 (online) / £78 (paper)"
        ),
        EntityTypeInfo(
            id="llp",
            title="Limited Liability Partnership (LLP)",
            shortName="LLP",
            description="Partnership with limited liability. Combines flexibility of partnership with protection of limited company.",
            useCases=["Professional services (accountants, lawyers)", "Joint ventures", "Business partnerships wanting liability protection"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["Minimum 2 designated members", "Members taxed as self-employed", "Must file accounts and confirmation statement"],
            currentFee="£50 (online) / £71 (paper)",
            futureFee="£50 (online) / £78 (paper)"
        ),
        EntityTypeInfo(
            id="lp",
            title="Limited Partnership (LP)",
            shortName="LP",
            description="At least one general partner with unlimited liability and limited partners with limited liability.",
            useCases=["Investment funds", "Property investment", "Venture capital structures"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["General partner has unlimited liability", "Limited partners cannot manage business", "Different tax treatment"],
            currentFee="£20 (online) / £30 (paper)",
            futureFee="£20 (online) / £30 (paper)"
        ),
        EntityTypeInfo(
            id="cic",
            title="Community Interest Company (CIC)",
            shortName="CIC",
            description="Limited company for social enterprises. Must benefit community. Assets locked for community purposes.",
            useCases=["Social enterprises", "Community projects", "Businesses with social mission"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House (regulated by CIC Regulator)",
            isCompaniesHouse=True,
            constraints=["Asset lock - cannot distribute to shareholders", "Must pass community interest test", "Annual CIC report required", "Regulated by CIC Regulator"],
            currentFee="£27 (online) / £35 (paper)",
            futureFee="£27 (online) / £35 (paper)",
            feeNote="Conversion from existing company: £27 online / £35 paper"
        ),
        EntityTypeInfo(
            id="overseas",
            title="Overseas Company (UK Establishment)",
            shortName="UK Branch",
            description="Registration of a branch or place of business for a company incorporated outside the UK.",
            useCases=["Foreign companies operating in UK", "International expansion", "UK presence for overseas business"],
            registrationAuthority="companies_house",
            authorityLabel="Companies House",
            isCompaniesHouse=True,
            constraints=["Parent company must be incorporated abroad", "Must file accounts of parent company", "UK representative required"],
            currentFee="£20 (online) / £30 (paper)",
            futureFee="£20 (online) / £30 (paper)"
        ),
        EntityTypeInfo(
            id="royal_charter",
            title="Royal Charter Company",
            shortName="Royal Charter",
            description="Incorporated by Royal Charter granted by the monarch. Very rare, prestigious status.",
            useCases=["Professional bodies", "Universities", "Charities of national importance"],
            registrationAuthority="privy_council",
            authorityLabel="Privy Council (appears on Companies House register)",
            isCompaniesHouse=True,
            constraints=["Requires petition to Privy Council", "Must demonstrate national significance", "Very rare and difficult to obtain"],
            currentFee="Varies - petition process",
            futureFee="Varies - petition process",
            feeNote="Contact Privy Council for guidance"
        ),
        # NOT Companies House
        EntityTypeInfo(
            id="cio",
            title="Charitable Incorporated Organisation (CIO)",
            shortName="CIO",
            description="Legal structure designed specifically for charities. Not registered with Companies House.",
            useCases=["Charities", "Non-profit organisations with charitable purposes"],
            registrationAuthority="charity_commission",
            authorityLabel="Charity Commission (NOT Companies House)",
            isCompaniesHouse=False,
            constraints=["Must have exclusively charitable purposes", "Registered with Charity Commission only", "Simpler governance than company"],
            currentFee="Free to register",
            futureFee="Free to register",
            feeNote="Apply via Charity Commission website"
        ),
        EntityTypeInfo(
            id="coop",
            title="Co-operative / Community Benefit Society",
            shortName="Co-op/CBS",
            description="Owned and controlled by members. Operates for mutual benefit or community benefit.",
            useCases=["Worker co-operatives", "Consumer co-operatives", "Community shops", "Housing co-ops"],
            registrationAuthority="fca",
            authorityLabel="Financial Conduct Authority (NOT Companies House)",
            isCompaniesHouse=False,
            constraints=["Democratic member control", "Registered with FCA", "Profits distributed to members or reinvested"],
            currentFee="£40 (standard) / £40 (mutual)",
            futureFee="£40 (standard) / £40 (mutual)",
            feeNote="Apply via FCA Mutuals Public Register"
        ),
        EntityTypeInfo(
            id="sole_trader",
            title="Sole Trader",
            shortName="Sole Trader",
            description="Simplest business structure. You and the business are legally the same. No limited liability.",
            useCases=["Freelancers", "Small service businesses", "Testing business ideas", "Side businesses"],
            registrationAuthority="hmrc",
            authorityLabel="HMRC (NOT Companies House)",
            isCompaniesHouse=False,
            constraints=["Unlimited personal liability", "Personal and business finances not separated", "Must register for self-assessment"],
            currentFee="Free to register",
            futureFee="Free to register",
            feeNote="Register with HMRC for Self Assessment"
        ),
        EntityTypeInfo(
            id="partnership",
            title="General Partnership",
            shortName="Partnership",
            description="Two or more people running a business together. All partners share unlimited liability.",
            useCases=["Professional partnerships", "Small business partnerships", "Family businesses"],
            registrationAuthority="hmrc",
            authorityLabel="HMRC (NOT Companies House)",
            isCompaniesHouse=False,
            constraints=["Unlimited joint and several liability", "Partners taxed individually", "Must register partnership with HMRC"],
            currentFee="Free to register",
            futureFee="Free to register",
            feeNote="Register with HMRC"
        ),
    ]
    
    # Fee change notice
    FEE_CHANGE_NOTICE = {
        "title": "Companies House Fee Changes",
        "message": "Fees are changing from 1 February 2026. Current fees shown alongside future fees.",
        "currentEffectiveFrom": "2024-05-01",
        "futureEffectiveFrom": "2026-02-01",
        "source": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    @staticmethod
    def get_entity_types() -> List[dict]:
        """Get all entity types with full information"""
        return [et.model_dump() for et in CompanyProfileService.ENTITY_TYPES]
    
    @staticmethod
    def get_fee_notice() -> dict:
        """Get fee change notice"""
        return CompanyProfileService.FEE_CHANGE_NOTICE
    
    @staticmethod
    async def create_profile(workspace_id: str, user_id: str, data: CompanyProfileCreate) -> dict:
        """Create a new company profile"""
        db = get_db()
        
        # Check if profile already exists for workspace
        existing = await db.company_profiles.find_one({"workspaceId": workspace_id})
        if existing:
            # Update instead of create
            return await CompanyProfileService.update_profile(existing["id"], workspace_id, data)
        
        profile_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        profile = {
            "id": profile_id,
            "workspaceId": workspace_id,
            "entityType": data.entityType,
            "isRegistrationConfirmed": False,
            "proposedName": data.proposedName,
            "legalNameConfirmed": False,
            "legalName": None,
            "nameCheckedAt": None,
            "nameCheckResults": None,
            "businessDescription": data.businessDescription,
            "selectedSicCodes": data.selectedSicCodes,
            "targetMarket": data.targetMarket,
            "fundingGoal": data.fundingGoal,
            "registrationData": {},
            "officialProfile": None,
            "operatingProfile": {},
            "derivedProfile": {},
            "created_by": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.company_profiles.insert_one(profile)
        return {k: v for k, v in profile.items() if k != '_id'}
    
    @staticmethod
    async def get_profile(workspace_id: str) -> Optional[dict]:
        """Get company profile for workspace"""
        db = get_db()
        profile = await db.company_profiles.find_one({"workspaceId": workspace_id})
        if profile:
            return {k: v for k, v in profile.items() if k != '_id'}
        return None
    
    @staticmethod
    async def update_profile(profile_id: str, workspace_id: str, data: dict) -> dict:
        """Update company profile"""
        db = get_db()
        
        profile = await db.company_profiles.find_one({
            "id": profile_id,
            "workspaceId": workspace_id
        })
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Flatten update data
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else dict(data)
        
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        await db.company_profiles.update_one(
            {"id": profile_id},
            {"$set": update_data}
        )
        
        updated = await db.company_profiles.find_one({"id": profile_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def save_registration_data(workspace_id: str, registration_data: dict) -> dict:
        """Save registration wizard data"""
        db = get_db()
        
        profile = await db.company_profiles.find_one({"workspaceId": workspace_id})
        
        if not profile:
            # Create new profile
            profile_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            profile = {
                "id": profile_id,
                "workspaceId": workspace_id,
                "registrationData": registration_data,
                "createdAt": now,
                "updatedAt": now
            }
            await db.company_profiles.insert_one(profile)
        else:
            # Update existing
            await db.company_profiles.update_one(
                {"workspaceId": workspace_id},
                {
                    "$set": {
                        "registrationData": registration_data,
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            profile = await db.company_profiles.find_one({"workspaceId": workspace_id})
        
        return {k: v for k, v in profile.items() if k != '_id'}
    
    @staticmethod
    async def lock_company_name(workspace_id: str, name: str, check_results: dict) -> dict:
        """Lock the confirmed company name"""
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()
        
        update_data = {
            "legalNameConfirmed": True,
            "legalName": name,
            "nameCheckedAt": now,
            "nameCheckResults": check_results,
            "updatedAt": now
        }
        
        profile = await db.company_profiles.find_one({"workspaceId": workspace_id})
        if profile:
            await db.company_profiles.update_one(
                {"workspaceId": workspace_id},
                {"$set": update_data}
            )
        else:
            update_data["id"] = str(uuid.uuid4())
            update_data["workspaceId"] = workspace_id
            update_data["createdAt"] = now
            await db.company_profiles.insert_one(update_data)
        
        profile = await db.company_profiles.find_one({"workspaceId": workspace_id})
        return {k: v for k, v in profile.items() if k != '_id'}
    
    # === COMPANIES HOUSE API INTEGRATION ===
    
    @staticmethod
    async def check_name_availability(name: str) -> NameSearchResult:
        """Check company name availability using Companies House API"""
        now = datetime.now(timezone.utc).isoformat()
        
        if not CH_API_KEY:
            # Return mock result if no API key
            return NameSearchResult(
                searchedName=name,
                isAvailable=True,
                confidence=0.0,
                exactMatches=[],
                similarMatches=[],
                suggestions=[],
                checkedAt=now
            )
        
        try:
            async with httpx.AsyncClient() as client:
                # Search for similar company names
                search_url = f"{CH_API_BASE}/search/companies"
                response = await client.get(
                    search_url,
                    params={
                        "q": name,
                        "items_per_page": 20
                    },
                    auth=(CH_API_KEY, ""),
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"API error: {response.status_code}")
                
                data = response.json()
                items = data.get("items", [])
                
                # Analyze results
                exact_matches = []
                similar_matches = []
                search_name_lower = name.lower().replace(" ltd", "").replace(" limited", "").strip()
                
                for item in items:
                    company_name = item.get("title", "")
                    company_name_lower = company_name.lower().replace(" ltd", "").replace(" limited", "").strip()
                    
                    match_info = {
                        "companyName": company_name,
                        "companyNumber": item.get("company_number"),
                        "companyStatus": item.get("company_status"),
                        "companyType": item.get("company_type"),
                        "incorporationDate": item.get("date_of_creation")
                    }
                    
                    if company_name_lower == search_name_lower:
                        exact_matches.append(match_info)
                    elif search_name_lower in company_name_lower or company_name_lower in search_name_lower:
                        similar_matches.append(match_info)
                    else:
                        similar_matches.append(match_info)
                
                # Calculate availability
                is_available = len(exact_matches) == 0
                confidence = 0.9 if len(items) > 0 else 0.7
                
                # Generate suggestions if not available
                suggestions = []
                if not is_available or len(similar_matches) > 5:
                    suggestions = await CompanyProfileService._generate_name_suggestions(name)
                
                return NameSearchResult(
                    searchedName=name,
                    isAvailable=is_available,
                    confidence=confidence,
                    exactMatches=exact_matches[:5],
                    similarMatches=similar_matches[:10],
                    suggestions=suggestions,
                    checkedAt=now
                )
                
        except Exception as e:
            print(f"Companies House API error: {e}")
            # Return result with error indication
            return NameSearchResult(
                searchedName=name,
                isAvailable=True,
                confidence=0.0,
                exactMatches=[],
                similarMatches=[],
                suggestions=[],
                checkedAt=now
            )
    
    @staticmethod
    async def _generate_name_suggestions(original_name: str) -> List[NameSuggestion]:
        """Generate AI name suggestions"""
        if not LLM_AVAILABLE:
            return CompanyProfileService._get_fallback_suggestions(original_name)
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return CompanyProfileService._get_fallback_suggestions(original_name)
            
            prompt = f"""Generate 10 alternative company name suggestions based on: "{original_name}"
            
            Requirements:
            - Must be unique and professional
            - Follow UK Companies House naming rules
            - Avoid restricted words (Bank, Royal, British, etc.) unless noting permission needed
            - Provide variety: descriptors, abbreviations, word stems, variations
            
            Return JSON array with objects containing:
            - name: the suggested company name (without Ltd suffix)
            - reason: brief explanation
            - type: one of "descriptor", "abbreviation", "stem", "variation"
            
            Return ONLY valid JSON array."""
            
            chat = LlmChat(
                api_key=llm_key,
                model="gpt-4o",
                system_message="You are a company naming expert. Return only valid JSON."
            )
            
            response = await chat.send_async(message=UserMessage(text=prompt))
            
            import json
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            suggestions_data = json.loads(text.strip())
            return [
                NameSuggestion(
                    name=s.get("name", ""),
                    reason=s.get("reason", ""),
                    type=s.get("type", "variation")
                )
                for s in suggestions_data[:12]
            ]
            
        except Exception as e:
            print(f"Name suggestion error: {e}")
            return CompanyProfileService._get_fallback_suggestions(original_name)
    
    @staticmethod
    def _get_fallback_suggestions(name: str) -> List[NameSuggestion]:
        """Fallback name suggestions"""
        base = name.replace(" Ltd", "").replace(" Limited", "").strip()
        words = base.split()
        
        suggestions = [
            NameSuggestion(name=f"{base} Solutions", reason="Added industry descriptor", type="descriptor"),
            NameSuggestion(name=f"{base} Group", reason="Added corporate descriptor", type="descriptor"),
            NameSuggestion(name=f"{base} UK", reason="Added location identifier", type="descriptor"),
            NameSuggestion(name=f"{base} International", reason="Added global scope", type="descriptor"),
        ]
        
        if len(words) > 1:
            initials = "".join([w[0].upper() for w in words])
            suggestions.append(NameSuggestion(name=initials, reason="Initials abbreviation", type="abbreviation"))
            suggestions.append(NameSuggestion(name=f"{initials} {words[-1]}", reason="Initials with last word", type="abbreviation"))
        
        suggestions.extend([
            NameSuggestion(name=f"{base} Ventures", reason="Added business descriptor", type="descriptor"),
            NameSuggestion(name=f"{base} Partners", reason="Added partnership descriptor", type="descriptor"),
            NameSuggestion(name=f"The {base} Company", reason="Classic company name format", type="variation"),
            NameSuggestion(name=f"{base} Co", reason="Abbreviated company suffix", type="abbreviation"),
        ])
        
        return suggestions[:12]
    
    @staticmethod
    async def confirm_registration(workspace_id: str, data: RegistrationConfirmRequest) -> dict:
        """Confirm registration by fetching company details from Companies House"""
        if not CH_API_KEY:
            return {
                "success": False,
                "message": "Companies House API key not configured. Please enter company details manually.",
                "companyData": None
            }
        
        try:
            async with httpx.AsyncClient() as client:
                # Fetch company profile
                profile_url = f"{CH_API_BASE}/company/{data.companyNumber}"
                response = await client.get(
                    profile_url,
                    auth=(CH_API_KEY, ""),
                    timeout=30.0
                )
                
                if response.status_code == 404:
                    return {
                        "success": False,
                        "message": f"Company number {data.companyNumber} not found. Please check and try again.",
                        "companyData": None
                    }
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "message": f"Failed to fetch company details. Please try again later.",
                        "companyData": None
                    }
                
                company_data = response.json()
                
                # Verify postcode if provided
                if data.postcode:
                    registered_office = company_data.get("registered_office_address", {})
                    ch_postcode = registered_office.get("postal_code", "").replace(" ", "").upper()
                    input_postcode = data.postcode.replace(" ", "").upper()
                    
                    if ch_postcode and input_postcode and ch_postcode != input_postcode:
                        return {
                            "success": False,
                            "message": "Postcode does not match registered office. Please verify your company number.",
                            "companyData": None
                        }
                
                # Build official profile
                official_profile = {
                    "companyNumber": company_data.get("company_number"),
                    "companyName": company_data.get("company_name"),
                    "companyStatus": company_data.get("company_status"),
                    "companyType": company_data.get("type"),
                    "incorporationDate": company_data.get("date_of_creation"),
                    "sicCodes": company_data.get("sic_codes", []),
                    "registeredOffice": company_data.get("registered_office_address"),
                    "confirmationStatementDue": company_data.get("confirmation_statement", {}).get("next_due"),
                    "accountsDue": company_data.get("accounts", {}).get("next_due"),
                    "lastRefreshed": datetime.now(timezone.utc).isoformat()
                }
                
                # Save to database
                db = get_db()
                now = datetime.now(timezone.utc).isoformat()
                
                await db.company_profiles.update_one(
                    {"workspaceId": workspace_id},
                    {
                        "$set": {
                            "isRegistrationConfirmed": True,
                            "legalName": company_data.get("company_name"),
                            "legalNameConfirmed": True,
                            "officialProfile": official_profile,
                            "updatedAt": now
                        }
                    },
                    upsert=True
                )
                
                return {
                    "success": True,
                    "message": "Company registration confirmed successfully!",
                    "companyData": official_profile
                }
                
        except Exception as e:
            print(f"Registration confirmation error: {e}")
            return {
                "success": False,
                "message": f"Failed to verify company: {str(e)}",
                "companyData": None
            }
    
    @staticmethod
    async def refresh_official_profile(workspace_id: str) -> dict:
        """Refresh official profile from Companies House"""
        db = get_db()
        profile = await db.company_profiles.find_one({"workspaceId": workspace_id})
        
        if not profile or not profile.get("officialProfile"):
            raise HTTPException(status_code=404, detail="No confirmed registration found")
        
        company_number = profile["officialProfile"].get("companyNumber")
        if not company_number:
            raise HTTPException(status_code=400, detail="Company number not found")
        
        result = await CompanyProfileService.confirm_registration(
            workspace_id,
            RegistrationConfirmRequest(companyNumber=company_number)
        )
        
        if result["success"]:
            updated = await db.company_profiles.find_one({"workspaceId": workspace_id})
            return {k: v for k, v in updated.items() if k != '_id'}
        
        raise HTTPException(status_code=400, detail=result["message"])
