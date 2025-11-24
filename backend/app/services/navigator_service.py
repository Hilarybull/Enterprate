"""Navigator service for invoicing"""
from fastapi import HTTPException
from app.core.database import get_database
from app.schemas.invoice import Invoice, InvoiceCreate, InvoiceUpdate
from app.schemas.intelligence import IntelligenceEvent

class NavigatorService:
    """Service for Navigator invoicing features"""
    
    @staticmethod
    async def get_invoices(workspace_id: str) -> list:
        """Get all invoices for a workspace"""
        db = get_database()
        invoices = await db.invoices.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
        return invoices
    
    @staticmethod
    async def create_invoice(invoice_data: InvoiceCreate, workspace_id: str, user_id: str) -> dict:
        """Create a new invoice"""
        db = get_database()
        
        invoice = Invoice(
            workspaceId=workspace_id,
            **invoice_data.model_dump()
        )
        
        doc = invoice.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        if doc['dueDate']:
            doc['dueDate'] = doc['dueDate'].isoformat()
        await db.invoices.insert_one(doc)
        
        # Log event
        event = IntelligenceEvent(
            workspaceId=workspace_id,
            userId=user_id,
            type="navigator.invoice_created",
            payload={"invoiceId": invoice.id, "amount": invoice.amount}
        )
        event_doc = event.model_dump()
        event_doc['occurredAt'] = event_doc['occurredAt'].isoformat()
        await db.intelligence_events.insert_one(event_doc)
        
        return invoice.model_dump()
    
    @staticmethod
    async def update_invoice(invoice_id: str, invoice_data: InvoiceUpdate, workspace_id: str) -> dict:
        """Update an invoice"""
        db = get_database()
        
        update_data = {k: v for k, v in invoice_data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        await db.invoices.update_one(
            {"id": invoice_id, "workspaceId": workspace_id},
            {"$set": update_data}
        )
        
        invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
        return invoice
