"""Intelligence Graph Service - Tracks user activities and generated assets"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.core.database import get_db


class IntelligenceEvent(BaseModel):
    """Model for intelligence events"""
    eventType: str
    entityType: str
    entityId: Optional[str] = None
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class IntelligenceGraphService:
    """Service for logging and analyzing user activities"""
    
    # Event types for categorization
    EVENT_CATEGORIES = {
        "catalogue": ["item_added", "item_updated", "item_deleted", "upload_processed", "bulk_added"],
        "invoice": ["created", "updated", "finalized", "sent", "paid", "overdue", "pdf_generated"],
        "document": ["generated", "edited", "saved", "exported", "deleted"],
        "expense": ["created", "updated", "deleted", "receipt_uploaded", "categorized"],
        "customer": ["created", "updated", "deleted", "contacted", "converted"],
        "website": ["generated", "published", "updated", "lead_captured", "analytics_viewed"],
        "brand": ["logo_uploaded", "colors_updated", "asset_created"],
        "finance": ["tax_calculated", "report_generated", "autofill_used"],
        "team": ["member_invited", "member_joined", "role_changed", "member_removed"],
        "integration": ["connected", "disconnected", "synced", "error"]
    }
    
    @staticmethod
    async def log_event(
        workspace_id: str,
        user_id: str,
        event_type: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Log an intelligence event"""
        db = get_db()
        
        event_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        event = {
            "id": event_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "eventType": event_type,
            "entityType": entity_type,
            "entityId": entity_id,
            "data": data or {},
            "metadata": metadata or {},
            "occurredAt": now,
            "createdAt": now
        }
        
        await db.intelligence_events.insert_one(event)
        
        # Update workspace activity summary
        await IntelligenceGraphService._update_activity_summary(workspace_id, entity_type, event_type)
        
        return {k: v for k, v in event.items() if k != '_id'}
    
    @staticmethod
    async def _update_activity_summary(workspace_id: str, entity_type: str, event_type: str):
        """Update workspace activity summary for quick insights"""
        db = get_db()
        
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        month = now.strftime("%Y-%m")
        
        # Update daily count
        await db.activity_summaries.update_one(
            {"workspace_id": workspace_id, "period": today, "period_type": "daily"},
            {
                "$inc": {
                    f"counts.{entity_type}.{event_type}": 1,
                    f"counts.{entity_type}.total": 1,
                    "counts.total": 1
                },
                "$set": {"updatedAt": now.isoformat()}
            },
            upsert=True
        )
        
        # Update monthly count
        await db.activity_summaries.update_one(
            {"workspace_id": workspace_id, "period": month, "period_type": "monthly"},
            {
                "$inc": {
                    f"counts.{entity_type}.{event_type}": 1,
                    f"counts.{entity_type}.total": 1,
                    "counts.total": 1
                },
                "$set": {"updatedAt": now.isoformat()}
            },
            upsert=True
        )
    
    @staticmethod
    async def get_events(
        workspace_id: str,
        entity_type: Optional[str] = None,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[dict]:
        """Get intelligence events with filters"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        
        if entity_type:
            query["entityType"] = entity_type
        if event_type:
            # Support both old 'type' and new 'eventType' field names
            query["$or"] = [{"eventType": event_type}, {"type": event_type}]
        if entity_id:
            query["entityId"] = entity_id
        if start_date:
            query["occurredAt"] = {"$gte": start_date}
        if end_date:
            if "occurredAt" in query:
                query["occurredAt"]["$lte"] = end_date
            else:
                query["occurredAt"] = {"$lte": end_date}
        
        events = await db.intelligence_events.find(query)\
            .sort("occurredAt", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(length=limit)
        
        return [{k: v for k, v in e.items() if k != '_id'} for e in events]
    
    @staticmethod
    async def get_activity_summary(
        workspace_id: str,
        period_type: str = "daily",
        periods: int = 7
    ) -> List[dict]:
        """Get activity summary for dashboard"""
        db = get_db()
        
        summaries = await db.activity_summaries.find({
            "workspace_id": workspace_id,
            "period_type": period_type
        }).sort("period", -1).limit(periods).to_list(length=periods)
        
        return [{k: v for k, v in s.items() if k != '_id'} for s in summaries]
    
    @staticmethod
    async def get_entity_timeline(
        workspace_id: str,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[dict]:
        """Get complete timeline for a specific entity"""
        db = get_db()
        
        events = await db.intelligence_events.find({
            "workspace_id": workspace_id,
            "entityType": entity_type,
            "entityId": entity_id
        }).sort("occurredAt", -1).limit(limit).to_list(length=limit)
        
        return [{k: v for k, v in e.items() if k != '_id'} for e in events]
    
    @staticmethod
    async def get_insights(workspace_id: str) -> dict:
        """Get aggregated insights for the workspace"""
        db = get_db()
        
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        month = now.strftime("%Y-%m")
        
        # Get today's summary
        today_summary = await db.activity_summaries.find_one({
            "workspace_id": workspace_id,
            "period": today,
            "period_type": "daily"
        })
        
        # Get monthly summary
        month_summary = await db.activity_summaries.find_one({
            "workspace_id": workspace_id,
            "period": month,
            "period_type": "monthly"
        })
        
        # Get recent events
        recent_events = await db.intelligence_events.find({
            "workspace_id": workspace_id
        }).sort("occurredAt", -1).limit(10).to_list(length=10)
        
        # Count entities
        entity_counts = {}
        for entity_type in ["catalogue", "invoice", "document", "expense", "customer"]:
            collection_map = {
                "catalogue": "catalogue_items",
                "invoice": "invoices",
                "document": "business_documents",
                "expense": "expenses",
                "customer": "customers"
            }
            collection = collection_map.get(entity_type)
            if collection:
                count = await db[collection].count_documents({"workspace_id": workspace_id})
                entity_counts[entity_type] = count
        
        return {
            "today": {
                "total": today_summary.get("counts", {}).get("total", 0) if today_summary else 0,
                "breakdown": today_summary.get("counts", {}) if today_summary else {}
            },
            "month": {
                "total": month_summary.get("counts", {}).get("total", 0) if month_summary else 0,
                "breakdown": month_summary.get("counts", {}) if month_summary else {}
            },
            "entityCounts": entity_counts,
            "recentActivity": [{k: v for k, v in e.items() if k != '_id'} for e in recent_events]
        }
    
    @staticmethod
    async def get_entity_stats(workspace_id: str, entity_type: str) -> dict:
        """Get statistics for a specific entity type"""
        db = get_db()
        
        # Pipeline to aggregate events by event_type for the entity
        pipeline = [
            {"$match": {"workspace_id": workspace_id, "entityType": entity_type}},
            {"$group": {
                "_id": "$eventType",
                "count": {"$sum": 1},
                "lastOccurred": {"$max": "$occurredAt"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = await db.intelligence_events.aggregate(pipeline).to_list(length=50)
        
        return {
            "entityType": entity_type,
            "eventBreakdown": [
                {"eventType": r["_id"], "count": r["count"], "lastOccurred": r["lastOccurred"]}
                for r in results
            ]
        }


# Helper functions for common logging patterns
async def log_catalogue_event(workspace_id: str, user_id: str, event_type: str, item_id: str = None, data: dict = None):
    """Log catalogue-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="catalogue",
        entity_id=item_id,
        data=data
    )


async def log_invoice_event(workspace_id: str, user_id: str, event_type: str, invoice_id: str = None, data: dict = None):
    """Log invoice-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="invoice",
        entity_id=invoice_id,
        data=data
    )


async def log_document_event(workspace_id: str, user_id: str, event_type: str, doc_id: str = None, data: dict = None):
    """Log document-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="document",
        entity_id=doc_id,
        data=data
    )


async def log_expense_event(workspace_id: str, user_id: str, event_type: str, expense_id: str = None, data: dict = None):
    """Log expense-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="expense",
        entity_id=expense_id,
        data=data
    )


async def log_customer_event(workspace_id: str, user_id: str, event_type: str, customer_id: str = None, data: dict = None):
    """Log customer-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="customer",
        entity_id=customer_id,
        data=data
    )


async def log_website_event(workspace_id: str, user_id: str, event_type: str, website_id: str = None, data: dict = None):
    """Log website-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="website",
        entity_id=website_id,
        data=data
    )


async def log_brand_event(workspace_id: str, user_id: str, event_type: str, asset_id: str = None, data: dict = None):
    """Log brand-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="brand",
        entity_id=asset_id,
        data=data
    )


async def log_finance_event(workspace_id: str, user_id: str, event_type: str, data: dict = None):
    """Log finance-related events"""
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user_id,
        event_type=event_type,
        entity_type="finance",
        data=data
    )
