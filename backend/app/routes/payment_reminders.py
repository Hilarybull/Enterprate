"""Payment Reminder Routes"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access
from app.services.payment_reminder_service import PaymentReminderService

router = APIRouter(prefix="/invoices/reminders", tags=["payment-reminders"])


class MarkPaidRequest(BaseModel):
    paymentDate: Optional[str] = None
    paymentMethod: Optional[str] = None


@router.get("/summary")
async def get_payment_summary(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get payment status summary"""
    await verify_workspace_access(workspace_id, user)
    return await PaymentReminderService.get_payment_summary(workspace_id)


@router.get("/pending")
async def get_pending_reminders(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get invoices that need payment reminders"""
    await verify_workspace_access(workspace_id, user)
    return await PaymentReminderService.get_invoices_needing_reminders(workspace_id)


@router.post("/process")
async def process_reminders(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Process and send all due reminders for the workspace"""
    await verify_workspace_access(workspace_id, user)
    return await PaymentReminderService.process_all_reminders(workspace_id)


@router.post("/{invoice_id}/send")
async def send_reminder(
    invoice_id: str,
    reminder_type: str = Query("first_overdue", enum=["before_due", "on_due_date", "first_overdue", "second_overdue", "final_notice"]),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Manually send a payment reminder for an invoice"""
    await verify_workspace_access(workspace_id, user)
    return await PaymentReminderService.send_payment_reminder(invoice_id, workspace_id, reminder_type)


@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: str,
    data: MarkPaidRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Mark an invoice as paid"""
    await verify_workspace_access(workspace_id, user)
    return await PaymentReminderService.mark_invoice_paid(
        invoice_id, 
        workspace_id, 
        user["id"],
        data.paymentDate,
        data.paymentMethod
    )


@router.post("/update-overdue")
async def update_overdue_status(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update overdue status for all invoices"""
    await verify_workspace_access(workspace_id, user)
    return await PaymentReminderService.check_and_update_overdue_invoices(workspace_id)
