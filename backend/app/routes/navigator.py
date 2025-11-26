"""Navigator/Finance routes"""
from typing import List
from fastapi import APIRouter, Depends
from app.services.navigator_service import NavigatorService
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/navigator", tags=["navigator"])

@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    data: InvoiceCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new invoice"""
    await verify_workspace_access(workspace_id, user)
    return await NavigatorService.create_invoice(workspace_id, user["id"], data)

@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all invoices"""
    await verify_workspace_access(workspace_id, user)
    return await NavigatorService.get_invoices(workspace_id)

@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    data: InvoiceUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update an invoice"""
    await verify_workspace_access(workspace_id, user)
    return await NavigatorService.update_invoice(invoice_id, workspace_id, data)
