"""Business Blueprint routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from app.services.blueprint_service import BlueprintService
from app.schemas.blueprint import (
    BlueprintCreate, BlueprintUpdate, BlueprintResponse,
    BlueprintSectionResponse, SWOTAnalysis, FinancialProjection,
    BlueprintInputRequest, BlueprintGenerateRequest,
    BlueprintSectionUpdateRequest, BlueprintSectionRegenerateRequest
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/blueprint", tags=["blueprint"])


@router.post("", response_model=BlueprintResponse)
async def create_blueprint(
    data: BlueprintCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new business blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.create_blueprint(workspace_id, user["id"], data)


@router.get("", response_model=List[BlueprintResponse])
async def get_blueprints(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all blueprints for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_blueprints(workspace_id)


@router.get("/{blueprint_id}", response_model=BlueprintResponse)
async def get_blueprint(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a specific blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_blueprint(blueprint_id, workspace_id)


@router.post("/{blueprint_id}/generate-section/{section_type}")
async def generate_section(
    blueprint_id: str,
    section_type: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate a specific section using AI"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_section(workspace_id, blueprint_id, section_type)


@router.post("/{blueprint_id}/generate-swot")
async def generate_swot(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate SWOT analysis using AI"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_swot(workspace_id, blueprint_id)


@router.post("/{blueprint_id}/generate-financials")
async def generate_financials(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate financial projections"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_financials(workspace_id, blueprint_id)


@router.post("/{blueprint_id}/generate-full")
async def generate_full_blueprint(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate complete blueprint with all sections"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_full_blueprint(workspace_id, blueprint_id)


@router.patch("/{blueprint_id}", response_model=BlueprintResponse)
async def update_blueprint(
    blueprint_id: str,
    data: BlueprintUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.update_blueprint(blueprint_id, workspace_id, data)


@router.delete("/{blueprint_id}")
async def delete_blueprint(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a blueprint"""
    await verify_workspace_access(workspace_id, user)
    deleted = await BlueprintService.delete_blueprint(blueprint_id, workspace_id)
    return {"deleted": deleted}


@router.post("/generate-document")
async def generate_document(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate business document (quote, contract, policy, etc.) using AI"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_document(data)


@router.get("/module2/eligibility")
async def get_blueprint_eligibility(
    business_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Check readiness of all Module 2 blueprint outputs for a business context."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_eligibility(workspace_id, business_id)


@router.get("/module2/readiness/{document_type}")
async def get_document_readiness(
    document_type: str,
    business_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Readiness check for a specific blueprint document type."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_document_readiness(workspace_id, document_type, business_id)


@router.post("/module2/input")
async def save_blueprint_input(
    data: BlueprintInputRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Store missing structured document-context inputs."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.save_document_inputs(
        workspace_id=workspace_id,
        user_id=user["id"],
        document_type=data.documentType.value if hasattr(data.documentType, "value") else str(data.documentType),
        inputs=data.inputs or {},
        provenance=data.provenance or {},
        business_id=data.businessId,
    )


@router.post("/module2/generate")
async def generate_module2_document(
    data: BlueprintGenerateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate a Module 2 document from deterministic state + templates."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_module2_document(
        workspace_id=workspace_id,
        user_id=user["id"],
        document_type=data.documentType.value if hasattr(data.documentType, "value") else str(data.documentType),
        business_id=data.businessId,
        regenerate=data.regenerate,
    )


@router.get("/module2/document/{document_id}")
async def get_blueprint_document(
    document_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get generated blueprint draft document."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_document(workspace_id, document_id)


@router.post("/module2/document/{document_id}/edit")
async def edit_blueprint_document_section(
    document_id: str,
    data: BlueprintSectionUpdateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Save narrative edits for a section without recalculation."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.update_document_section(
        workspace_id=workspace_id,
        user_id=user["id"],
        document_id=document_id,
        section_id=data.sectionId,
        content=data.content,
    )


@router.post("/module2/document/{document_id}/regenerate-section")
async def regenerate_blueprint_document_section(
    document_id: str,
    data: BlueprintSectionRegenerateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Regenerate only the selected section from structured source data."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.regenerate_document_section(
        workspace_id=workspace_id,
        document_id=document_id,
        section_id=data.sectionId,
    )


@router.post("/module2/document/{document_id}/duplicate")
async def duplicate_blueprint_document(
    document_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Duplicate a generated document as a new versionable draft."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.duplicate_document(workspace_id, user["id"], document_id)


@router.get("/module2/document/{document_id}/export")
async def export_blueprint_document(
    document_id: str,
    format: str = "html",
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Export blueprint document as HTML or text."""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.export_document(workspace_id, document_id, format)
