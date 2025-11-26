"""Navigator service for invoices and operations"""
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate

class NavigatorService:
    """Service for Navigator/Finance operations"""
    
    @staticmethod
    async def create_invoice(workspace_id: str, user_id: str, data: InvoiceCreate) -> dict:
        """Create a new invoice"""
        db = get_db()
        
        # Generate invoice number
        count = await db.invoices.count_documents({"workspace_id": workspace_id})
        invoice_number = f"INV-{count + 1:04d}"
        
        invoice_id = str(uuid.uuid4())
        invoice = {
            "id": invoice_id,
            "workspace_id": workspace_id,
            "invoiceNumber": invoice_number,
            "clientName": data.clientName,
            "clientEmail": data.clientEmail,
            "amount": data.amount,
            "description": data.description,
            "dueDate": data.dueDate,
            "status": "DRAFT",
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.invoices.insert_one(invoice)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "invoice.created",
            "data": {"invoice_id": invoice_id, "amount": data.amount},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        })
        
        return {k: v for k, v in invoice.items() if k != '_id'}
    
    @staticmethod
    async def get_invoices(workspace_id: str) -> List[dict]:
        """Get all invoices for a workspace"""
        db = get_db()
        
        invoices = await db.invoices.find(
            {"workspace_id": workspace_id}
        ).sort("created_at", -1).to_list(length=100)
        
        return [{k: v for k, v in inv.items() if k != '_id'} for inv in invoices]
    
    @staticmethod
    async def update_invoice(invoice_id: str, workspace_id: str, data: InvoiceUpdate) -> dict:
        """Update an invoice"""
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await db.invoices.update_one(
                {"id": invoice_id},
                {"$set": update_data}
            )
        
        updated = await db.invoices.find_one({"id": invoice_id})
        return {k: v for k, v in updated.items() if k != '_id'}
