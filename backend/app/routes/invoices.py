"""Enhanced Invoice Routes with Catalogue Integration, PDF, and Email"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access
from app.services.invoice_service import (
    InvoiceService,
    EnhancedInvoiceCreate,
    InvoiceUpdateStatus,
    BrandAssetCreate,
    LineItem
)
import io

router = APIRouter(prefix="/invoices", tags=["invoices"])


class InvoiceUpdateRequest(BaseModel):
    clientName: Optional[str] = None
    clientEmail: Optional[str] = None
    clientAddress: Optional[str] = None
    lineItems: Optional[List[LineItem]] = None
    currency: Optional[str] = None
    dueDate: Optional[str] = None
    notes: Optional[str] = None
    termsAndConditions: Optional[str] = None
    status: Optional[str] = None


@router.get("")
async def get_invoices(
    status: Optional[str] = None,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all invoices with optional status filter"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.get_invoices(workspace_id, status)


@router.post("")
async def create_invoice(
    data: EnhancedInvoiceCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new invoice with line items from catalogue"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.create_invoice(workspace_id, user["id"], data)


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get single invoice details"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.get_invoice(invoice_id, workspace_id)


@router.patch("/{invoice_id}")
async def update_invoice(
    invoice_id: str,
    data: InvoiceUpdateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update invoice details"""
    await verify_workspace_access(workspace_id, user)
    update_data = data.model_dump(exclude_unset=True)
    
    # Recalculate totals if line items changed
    if "lineItems" in update_data and update_data["lineItems"]:
        subtotal = 0
        tax_total = 0
        line_items_data = []
        
        for item in update_data["lineItems"]:
            item_dict = item.model_dump() if hasattr(item, 'model_dump') else item
            item_subtotal = item_dict.get("quantity", 1) * item_dict.get("unitPrice", 0)
            item_tax = item_subtotal * (item_dict.get("taxRate", 0) / 100) if item_dict.get("taxRate") else 0
            
            line_items_data.append({
                "catalogueItemId": item_dict.get("catalogueItemId"),
                "name": item_dict.get("name"),
                "description": item_dict.get("description"),
                "quantity": item_dict.get("quantity", 1),
                "unitPrice": item_dict.get("unitPrice", 0),
                "taxRate": item_dict.get("taxRate"),
                "subtotal": round(item_subtotal, 2),
                "taxAmount": round(item_tax, 2),
                "total": round(item_subtotal + item_tax, 2)
            })
            
            subtotal += item_subtotal
            tax_total += item_tax
        
        update_data["lineItems"] = line_items_data
        update_data["subtotal"] = round(subtotal, 2)
        update_data["taxTotal"] = round(tax_total, 2)
        update_data["total"] = round(subtotal + tax_total, 2)
    
    return await InvoiceService.update_invoice(invoice_id, workspace_id, update_data)


@router.post("/{invoice_id}/finalize")
async def finalize_invoice(
    invoice_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Finalize invoice - move to pending_review status"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.finalize_invoice(invoice_id, workspace_id)


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate and download invoice PDF"""
    await verify_workspace_access(workspace_id, user)
    
    pdf_content = await InvoiceService.generate_pdf(invoice_id, workspace_id)
    
    # Get invoice for filename
    invoice = await InvoiceService.get_invoice(invoice_id, workspace_id)
    filename = f"{invoice.get('invoiceNumber', 'invoice')}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Send invoice via email"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.send_invoice_email(invoice_id, workspace_id, user["id"])


# Brand Assets
@router.get("/brand/assets")
async def get_brand_assets(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all brand assets"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.get_brand_assets(workspace_id)


@router.get("/brand/assets/{asset_type}")
async def get_brand_asset(
    asset_type: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get specific brand asset (e.g., logo)"""
    await verify_workspace_access(workspace_id, user)
    asset = await InvoiceService.get_brand_asset(workspace_id, asset_type)
    if not asset:
        return {"error": "Asset not found"}
    return asset


@router.post("/brand/assets")
async def save_brand_asset(
    data: BrandAssetCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Upload/update brand asset (logo)"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.save_brand_asset(workspace_id, user["id"], data)


@router.delete("/brand/assets/{asset_type}")
async def delete_brand_asset(
    asset_type: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete brand asset"""
    await verify_workspace_access(workspace_id, user)
    return await InvoiceService.delete_brand_asset(workspace_id, asset_type)
