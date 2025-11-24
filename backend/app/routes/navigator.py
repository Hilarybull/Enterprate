"""Navigator (invoicing) routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.services.navigator_service import NavigatorService
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access

router = APIRouter(prefix="/navigator", tags=["navigator"])

@router.get("/invoices")
async def get_invoices(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all invoices for a workspace"""
    await verify_workspace_access(workspace_id, user, db)
    return await NavigatorService.get_invoices(db, workspace_id)

@router.post("/invoices")
async def create_invoice(
    invoice_data: InvoiceCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new invoice"""
    await verify_workspace_access(workspace_id, user, db)
    return await NavigatorService.create_invoice(db, invoice_data, workspace_id, user['id'])

@router.patch("/invoices/{invoice_id}")
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an invoice"""
    await verify_workspace_access(workspace_id, user, db)
    return await NavigatorService.update_invoice(db, invoice_id, invoice_data, workspace_id)
