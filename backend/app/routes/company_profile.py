"""Company Profile routes - Central SSOT for company data"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.services.company_profile_service import CompanyProfileService
from app.services.fees_config_service import FeesConfigService
from app.schemas.company_profile import (
    CompanyProfileCreate, CompanyProfileUpdate, CompanyProfileResponse,
    NameSearchRequest, NameSearchResult, RegistrationConfirmRequest
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/company-profile", tags=["company-profile"])


@router.get("/entity-types")
async def get_entity_types():
    """Get all available entity types with full information"""
    return {
        "entityTypes": CompanyProfileService.get_entity_types(),
        "feeNotice": CompanyProfileService.get_fee_notice()
    }


@router.get("/fees")
async def get_registration_fees():
    """Get dynamic registration fees configuration from official sources"""
    return await FeesConfigService.get_all_fees()


@router.get("/fees/{business_type}")
async def get_fee_for_type(business_type: str):
    """Get fee for a specific business type"""
    fee = await FeesConfigService.get_fee_by_type(business_type)
    if not fee:
        return {"error": "Business type not found"}
    return fee


@router.get("/fees/companies-house/all")
async def get_companies_house_fees():
    """Get all Companies House registered business type fees"""
    return await FeesConfigService.get_companies_house_fees()


@router.get("/fees/other-authorities/all")
async def get_other_authority_fees():
    """Get fees for business types registered with other authorities"""
    return await FeesConfigService.get_other_authority_fees()


@router.post("", response_model=CompanyProfileResponse)
async def create_profile(
    data: CompanyProfileCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create or update company profile"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.create_profile(workspace_id, user["id"], data)


@router.get("", response_model=Optional[CompanyProfileResponse])
async def get_profile(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get company profile for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.get_profile(workspace_id)


@router.patch("", response_model=CompanyProfileResponse)
async def update_profile(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update company profile"""
    await verify_workspace_access(workspace_id, user)
    profile = await CompanyProfileService.get_profile(workspace_id)
    if not profile:
        # Create new profile
        return await CompanyProfileService.create_profile(workspace_id, user["id"], CompanyProfileCreate())
    return await CompanyProfileService.update_profile(profile["id"], workspace_id, data)


@router.post("/registration-data")
async def save_registration_data(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Save registration wizard data"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.save_registration_data(workspace_id, data)


@router.post("/check-name", response_model=NameSearchResult)
async def check_name_availability(
    data: NameSearchRequest,
    user: dict = Depends(get_current_user)
):
    """Check company name availability using Companies House API"""
    return await CompanyProfileService.check_name_availability(data.companyName)


@router.post("/lock-name")
async def lock_company_name(
    name: str = Query(...),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Lock confirmed company name"""
    await verify_workspace_access(workspace_id, user)
    
    # Check name one more time
    check_result = await CompanyProfileService.check_name_availability(name)
    
    return await CompanyProfileService.lock_company_name(
        workspace_id, 
        name, 
        check_result.model_dump()
    )


@router.post("/confirm-registration")
async def confirm_registration(
    data: RegistrationConfirmRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Confirm company registration by fetching from Companies House"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.confirm_registration(workspace_id, data)


@router.post("/refresh")
async def refresh_official_profile(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Refresh official profile from Companies House"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.refresh_official_profile(workspace_id)


@router.post("/generate-branding")
async def generate_branding(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate branding assets (logos, color suggestions) using AI"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.generate_branding(data)


@router.post("/generate-website-content")
async def generate_website_content(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate website content for a specific section"""
    await verify_workspace_access(workspace_id, user)
    return await CompanyProfileService.generate_website_content(data)
