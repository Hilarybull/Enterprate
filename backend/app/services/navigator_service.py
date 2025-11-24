"""Navigator service for invoicing"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.invoice import Invoice
from app.models.intelligence import IntelligenceEvent
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate

class NavigatorService:
    """Service for Navigator invoicing features"""
    
    @staticmethod
    async def get_invoices(db: AsyncSession, workspace_id: str) -> list:
        """Get all invoices for a workspace"""
        workspace_uuid = UUID(workspace_id)
        
        stmt = select(Invoice).where(Invoice.workspace_id == workspace_uuid)
        result = await db.execute(stmt)
        invoices = result.scalars().all()
        
        return [
            {
                "id": str(inv.id),
                "workspaceId": str(inv.workspace_id),
                "customerName": inv.customer_name,
                "amount": inv.amount,
                "currency": inv.currency,
                "status": inv.status.value,
                "dueDate": inv.due_date.isoformat() if inv.due_date else None,
                "items": inv.items,
                "createdAt": inv.created_at.isoformat()
            }
            for inv in invoices
        ]
    
    @staticmethod
    async def create_invoice(db: AsyncSession, invoice_data: InvoiceCreate, workspace_id: str, user_id: str) -> dict:
        """Create a new invoice"""
        workspace_uuid = UUID(workspace_id)
        user_uuid = UUID(user_id)
        
        invoice = Invoice(
            workspace_id=workspace_uuid,
            customer_name=invoice_data.customerName,
            amount=invoice_data.amount,
            currency=invoice_data.currency,
            due_date=invoice_data.dueDate,
            items=invoice_data.items
        )
        
        db.add(invoice)
        await db.flush()
        
        # Log event
        event = IntelligenceEvent(
            workspace_id=workspace_uuid,
            user_id=user_uuid,
            type="navigator.invoice_created",
            payload={"invoiceId": str(invoice.id), "amount": invoice.amount}
        )
        db.add(event)
        await db.flush()
        
        return {
            "id": str(invoice.id),
            "workspaceId": str(invoice.workspace_id),
            "customerName": invoice.customer_name,
            "amount": invoice.amount,
            "currency": invoice.currency,
            "status": invoice.status.value,
            "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "items": invoice.items,
            "createdAt": invoice.created_at.isoformat()
        }
    
    @staticmethod
    async def update_invoice(db: AsyncSession, invoice_id: str, invoice_data: InvoiceUpdate, workspace_id: str) -> dict:
        """Update an invoice"""
        invoice_uuid = UUID(invoice_id)
        workspace_uuid = UUID(workspace_id)
        
        update_data = {k: v for k, v in invoice_data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        stmt = select(Invoice).where(
            Invoice.id == invoice_uuid,
            Invoice.workspace_id == workspace_uuid
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Update fields - map camelCase to snake_case
        field_mapping = {
            "customerName": "customer_name",
            "dueDate": "due_date"
        }
        
        for key, value in update_data.items():
            db_field = field_mapping.get(key, key)
            if hasattr(invoice, db_field):
                setattr(invoice, db_field, value)
        
        await db.flush()
        
        return {
            "id": str(invoice.id),
            "workspaceId": str(invoice.workspace_id),
            "customerName": invoice.customer_name,
            "amount": invoice.amount,
            "currency": invoice.currency,
            "status": invoice.status.value,
            "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "items": invoice.items,
            "createdAt": invoice.created_at.isoformat()
        }
