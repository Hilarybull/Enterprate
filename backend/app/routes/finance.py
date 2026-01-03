"""Finance & Compliance routes - Consolidated finance operations including invoices"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.services.finance_service import FinanceService
from app.services.navigator_service import NavigatorService
from app.schemas.finance import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    ReceiptScanRequest, ReceiptScanResponse,
    TaxEstimateRequest, TaxEstimateResponse,
    ComplianceChecklistCreate, ComplianceChecklistUpdate, ComplianceChecklistResponse
)
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/finance", tags=["finance"])


# === INVOICE ENDPOINTS (Consolidated from Navigator) ===

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


# === EXPENSE ENDPOINTS ===

@router.post("/expenses", response_model=ExpenseResponse)
async def create_expense(
    data: ExpenseCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new expense"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.create_expense(workspace_id, user["id"], data)


@router.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    category: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all expenses"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.get_expenses(workspace_id, category)


@router.patch("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update an expense"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.update_expense(expense_id, workspace_id, data)


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete an expense"""
    await verify_workspace_access(workspace_id, user)
    deleted = await FinanceService.delete_expense(expense_id, workspace_id)
    return {"deleted": deleted}


@router.get("/expenses/summary")
async def get_expense_summary(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get expense summary statistics"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.get_expense_summary(workspace_id)


# === RECEIPT SCANNING ===

@router.post("/scan-receipt", response_model=ReceiptScanResponse)
async def scan_receipt(
    data: ReceiptScanRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Scan receipt image and extract data using AI Vision"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.scan_receipt(workspace_id, data)


# === TAX ESTIMATION ===

@router.post("/estimate-tax", response_model=TaxEstimateResponse)
async def estimate_tax(
    data: TaxEstimateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Estimate tax based on revenue and expenses"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.estimate_tax(workspace_id, data)


# === COMPLIANCE CHECKLIST ===

@router.post("/compliance", response_model=ComplianceChecklistResponse)
async def create_compliance_item(
    data: ComplianceChecklistCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a compliance checklist item"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.create_compliance_item(workspace_id, user["id"], data)


@router.get("/compliance", response_model=List[ComplianceChecklistResponse])
async def get_compliance_items(
    category: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get compliance checklist items"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.get_compliance_items(workspace_id, category)


@router.patch("/compliance/{item_id}", response_model=ComplianceChecklistResponse)
async def update_compliance_item(
    item_id: str,
    data: ComplianceChecklistUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a compliance item"""
    await verify_workspace_access(workspace_id, user)
    return await FinanceService.update_compliance_item(item_id, workspace_id, data)


@router.delete("/compliance/{item_id}")
async def delete_compliance_item(
    item_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a compliance item"""
    await verify_workspace_access(workspace_id, user)
    deleted = await FinanceService.delete_compliance_item(item_id, workspace_id)
    return {"deleted": deleted}


@router.get("/compliance/defaults")
async def get_default_compliance(
    business_type: str = Query("ltd"),
    user: dict = Depends(get_current_user)
):
    """Get default UK compliance checklist"""
    return await FinanceService.get_default_compliance_checklist(business_type)
