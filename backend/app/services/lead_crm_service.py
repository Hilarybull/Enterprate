"""Lead Capture to CRM Integration Service"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.core.database import get_db
from app.services.intelligence_service import log_customer_event, log_website_event


class LeadCRMService:
    """Service for integrating website leads with the Growth/CRM module"""
    
    @staticmethod
    async def process_website_lead(
        workspace_id: str,
        website_id: str,
        lead_data: Dict[str, Any]
    ) -> dict:
        """Process a lead captured from a website and add to CRM"""
        db = get_db()
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Extract lead info
        name = lead_data.get("name", "")
        email = lead_data.get("email", "")
        phone = lead_data.get("phone", "")
        company = lead_data.get("company", "")
        message = lead_data.get("message", "")
        
        if not email:
            return {"success": False, "error": "Email is required"}
        
        # Check if contact already exists
        existing_contact = await db.contacts.find_one({
            "workspace_id": workspace_id,
            "email": email
        })
        
        if existing_contact:
            # Update existing contact with new lead info
            contact_id = existing_contact["id"]
            
            # Add to interaction history
            interactions = existing_contact.get("interactions", [])
            interactions.append({
                "type": "website_lead",
                "source": website_id,
                "message": message,
                "timestamp": now
            })
            
            await db.contacts.update_one(
                {"id": contact_id},
                {"$set": {
                    "interactions": interactions,
                    "lastContactedAt": now,
                    "updatedAt": now
                }}
            )
            
            # Log event
            await log_customer_event(
                workspace_id=workspace_id,
                user_id="system",
                event_type="lead_updated",
                customer_id=contact_id,
                data={
                    "email": email,
                    "source": "website",
                    "website_id": website_id
                }
            )
            
            return {
                "success": True,
                "action": "updated",
                "contact_id": contact_id,
                "message": "Existing contact updated with new lead"
            }
        
        # Create new contact
        contact_id = str(uuid.uuid4())
        
        # Parse name into first/last
        name_parts = name.split(" ", 1) if name else ["", ""]
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        contact = {
            "id": contact_id,
            "workspace_id": workspace_id,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "company": company,
            "source": "website",
            "sourceId": website_id,
            "status": "lead",
            "stage": "new",
            "tags": ["website-lead"],
            "notes": message,
            "interactions": [{
                "type": "website_lead",
                "source": website_id,
                "message": message,
                "timestamp": now
            }],
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.contacts.insert_one(contact)
        
        # Log events
        await log_customer_event(
            workspace_id=workspace_id,
            user_id="system",
            event_type="created",
            customer_id=contact_id,
            data={
                "email": email,
                "name": name,
                "source": "website",
                "website_id": website_id
            }
        )
        
        await log_website_event(
            workspace_id=workspace_id,
            user_id="system",
            event_type="lead_converted",
            website_id=website_id,
            data={
                "contact_id": contact_id,
                "email": email
            }
        )
        
        return {
            "success": True,
            "action": "created",
            "contact_id": contact_id,
            "message": "New contact created from website lead"
        }
    
    @staticmethod
    async def get_website_leads(workspace_id: str, website_id: str = None) -> List[dict]:
        """Get all leads from websites"""
        db = get_db()
        
        query = {
            "workspace_id": workspace_id,
            "source": "website"
        }
        
        if website_id:
            query["sourceId"] = website_id
        
        leads = await db.contacts.find(query).sort("createdAt", -1).to_list(length=500)
        
        return [{k: v for k, v in lead.items() if k != '_id'} for lead in leads]
    
    @staticmethod
    async def convert_lead_to_customer(contact_id: str, workspace_id: str, user_id: str) -> dict:
        """Convert a lead to a customer"""
        db = get_db()
        
        contact = await db.contacts.find_one({
            "id": contact_id,
            "workspace_id": workspace_id
        })
        
        if not contact:
            return {"success": False, "error": "Contact not found"}
        
        now = datetime.now(timezone.utc).isoformat()
        
        await db.contacts.update_one(
            {"id": contact_id},
            {"$set": {
                "status": "customer",
                "stage": "converted",
                "convertedAt": now,
                "convertedBy": user_id,
                "updatedAt": now
            }}
        )
        
        # Log event
        await log_customer_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type="converted",
            customer_id=contact_id,
            data={
                "email": contact.get("email"),
                "previousStatus": contact.get("status")
            }
        )
        
        return {"success": True, "message": "Lead converted to customer"}
    
    @staticmethod
    async def get_lead_analytics(workspace_id: str) -> dict:
        """Get lead analytics for dashboard"""
        db = get_db()
        
        # Count by source
        pipeline_source = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": "$source",
                "count": {"$sum": 1}
            }}
        ]
        
        # Count by status
        pipeline_status = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        # Count by stage
        pipeline_stage = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": "$stage",
                "count": {"$sum": 1}
            }}
        ]
        
        sources = await db.contacts.aggregate(pipeline_source).to_list(length=20)
        statuses = await db.contacts.aggregate(pipeline_status).to_list(length=20)
        stages = await db.contacts.aggregate(pipeline_stage).to_list(length=20)
        
        # Get recent leads
        recent = await db.contacts.find({
            "workspace_id": workspace_id,
            "source": "website"
        }).sort("createdAt", -1).limit(5).to_list(length=5)
        
        return {
            "bySource": {r["_id"]: r["count"] for r in sources if r["_id"]},
            "byStatus": {r["_id"]: r["count"] for r in statuses if r["_id"]},
            "byStage": {r["_id"]: r["count"] for r in stages if r["_id"]},
            "totalLeads": sum(r["count"] for r in statuses),
            "websiteLeads": next((r["count"] for r in sources if r["_id"] == "website"), 0),
            "recentLeads": [{k: v for k, v in l.items() if k != '_id'} for l in recent]
        }
