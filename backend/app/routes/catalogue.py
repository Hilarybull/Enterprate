"""Product/Service Catalogue Routes"""
from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel
from app.core.security import get_current_user, get_workspace_id
from app.services.catalogue_service import (
    CatalogueService, 
    CatalogueItemCreate, 
    CatalogueItemUpdate
)

router = APIRouter(prefix="/catalogue", tags=["catalogue"])


class BulkAddRequest(BaseModel):
    items: List[dict]


@router.get("")
async def get_catalogue_items(
    category: Optional[str] = None,
    search: Optional[str] = None,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all catalogue items for workspace"""
    return await CatalogueService.get_items(workspace_id, category, search)


@router.post("")
async def create_catalogue_item(
    data: CatalogueItemCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new catalogue item"""
    return await CatalogueService.create_item(workspace_id, user["id"], data)


@router.get("/{item_id}")
async def get_catalogue_item(
    item_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a single catalogue item"""
    return await CatalogueService.get_item(item_id, workspace_id)


@router.put("/{item_id}")
async def update_catalogue_item(
    item_id: str,
    data: CatalogueItemUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a catalogue item"""
    return await CatalogueService.update_item(item_id, workspace_id, data)


@router.delete("/{item_id}")
async def delete_catalogue_item(
    item_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a catalogue item"""
    return await CatalogueService.delete_item(item_id, workspace_id)


@router.post("/upload")
async def upload_catalogue(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Upload and process a catalogue file (CSV, Excel, PDF, Word)"""
    return await CatalogueService.process_upload(workspace_id, user["id"], file)


@router.post("/bulk")
async def bulk_add_items(
    data: BulkAddRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Add multiple validated items to catalogue"""
    return await CatalogueService.bulk_add_items(workspace_id, user["id"], data.items)
