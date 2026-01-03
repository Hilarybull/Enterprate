"""Campaign Automation Rules Service"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.core.database import get_db


class CampaignAutomationService:
    """
    Service for advanced campaign automation rules.
    Supports trigger-based actions, conditions, and automated workflows.
    """
    
    # Available triggers
    TRIGGERS = {
        "lead_created": {"label": "New Lead Created", "category": "leads"},
        "lead_status_changed": {"label": "Lead Status Changed", "category": "leads"},
        "lead_score_threshold": {"label": "Lead Score Reaches Threshold", "category": "leads"},
        "invoice_paid": {"label": "Invoice Paid", "category": "finance"},
        "invoice_overdue": {"label": "Invoice Overdue", "category": "finance"},
        "campaign_started": {"label": "Campaign Started", "category": "campaigns"},
        "campaign_ended": {"label": "Campaign Ended", "category": "campaigns"},
        "conversion_goal_reached": {"label": "Conversion Goal Reached", "category": "campaigns"},
        "low_engagement": {"label": "Low Engagement Detected", "category": "analytics"},
        "high_engagement": {"label": "High Engagement Detected", "category": "analytics"},
        "time_based": {"label": "Scheduled Time", "category": "scheduling"},
        "website_lead_captured": {"label": "Website Lead Captured", "category": "website"},
        "ab_test_winner": {"label": "A/B Test Winner Determined", "category": "testing"}
    }
    
    # Available actions
    ACTIONS = {
        "send_email": {"label": "Send Email", "requires": ["recipient", "template"]},
        "create_task": {"label": "Create Task", "requires": ["title", "assignee"]},
        "update_lead_status": {"label": "Update Lead Status", "requires": ["status"]},
        "add_lead_tag": {"label": "Add Tag to Lead", "requires": ["tag"]},
        "schedule_post": {"label": "Schedule Social Post", "requires": ["platform", "content"]},
        "start_campaign": {"label": "Start Campaign", "requires": ["campaign_id"]},
        "pause_campaign": {"label": "Pause Campaign", "requires": ["campaign_id"]},
        "send_notification": {"label": "Send Notification", "requires": ["user_id", "message"]},
        "webhook": {"label": "Call Webhook", "requires": ["url"]},
        "apply_ab_winner": {"label": "Apply A/B Test Winner", "requires": ["test_id"]},
        "increase_budget": {"label": "Increase Campaign Budget", "requires": ["campaign_id", "amount"]},
        "decrease_budget": {"label": "Decrease Campaign Budget", "requires": ["campaign_id", "amount"]}
    }
    
    # Condition operators
    OPERATORS = {
        "equals": "Equals",
        "not_equals": "Does Not Equal",
        "contains": "Contains",
        "not_contains": "Does Not Contain",
        "greater_than": "Greater Than",
        "less_than": "Less Than",
        "greater_or_equal": "Greater Than or Equal",
        "less_or_equal": "Less Than or Equal",
        "is_empty": "Is Empty",
        "is_not_empty": "Is Not Empty",
        "in_list": "Is In List",
        "not_in_list": "Is Not In List"
    }
    
    @staticmethod
    async def create_rule(
        workspace_id: str,
        user_id: str,
        name: str,
        description: str,
        trigger: dict,
        conditions: List[dict],
        actions: List[dict],
        is_active: bool = True,
        priority: int = 0
    ) -> dict:
        """
        Create a new automation rule.
        
        Args:
            trigger: {"type": "lead_created", "config": {...}}
            conditions: [{"field": "source", "operator": "equals", "value": "website"}]
            actions: [{"type": "send_email", "config": {"template": "welcome"}}]
        """
        db = get_db()
        
        # Validate trigger
        if trigger.get("type") not in CampaignAutomationService.TRIGGERS:
            raise HTTPException(status_code=400, detail="Invalid trigger type")
        
        # Validate actions
        for action in actions:
            if action.get("type") not in CampaignAutomationService.ACTIONS:
                raise HTTPException(status_code=400, detail=f"Invalid action type: {action.get('type')}")
        
        rule_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        rule = {
            "id": rule_id,
            "workspace_id": workspace_id,
            "name": name,
            "description": description,
            "trigger": trigger,
            "conditions": conditions,
            "actions": actions,
            "isActive": is_active,
            "priority": priority,
            "executionCount": 0,
            "lastExecuted": None,
            "createdBy": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.automation_rules.insert_one(rule)
        return {k: v for k, v in rule.items() if k != '_id'}
    
    @staticmethod
    async def get_rules(
        workspace_id: str,
        is_active: Optional[bool] = None,
        trigger_type: Optional[str] = None
    ) -> List[dict]:
        """Get automation rules for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if is_active is not None:
            query["isActive"] = is_active
        if trigger_type:
            query["trigger.type"] = trigger_type
        
        rules = await db.automation_rules.find(query)\
            .sort("priority", -1)\
            .to_list(length=100)
        
        return [{k: v for k, v in r.items() if k != '_id'} for r in rules]
    
    @staticmethod
    async def get_rule(rule_id: str, workspace_id: str) -> Optional[dict]:
        """Get a specific rule"""
        db = get_db()
        rule = await db.automation_rules.find_one({
            "id": rule_id,
            "workspace_id": workspace_id
        })
        return {k: v for k, v in rule.items() if k != '_id'} if rule else None
    
    @staticmethod
    async def update_rule(
        rule_id: str,
        workspace_id: str,
        updates: dict
    ) -> dict:
        """Update an automation rule"""
        db = get_db()
        
        updates["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        await db.automation_rules.update_one(
            {"id": rule_id, "workspace_id": workspace_id},
            {"$set": updates}
        )
        
        updated = await db.automation_rules.find_one({"id": rule_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_rule(rule_id: str, workspace_id: str) -> bool:
        """Delete an automation rule"""
        db = get_db()
        result = await db.automation_rules.delete_one({
            "id": rule_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def toggle_rule(rule_id: str, workspace_id: str, is_active: bool) -> dict:
        """Toggle rule active status"""
        return await CampaignAutomationService.update_rule(
            rule_id, workspace_id, {"isActive": is_active}
        )
    
    @staticmethod
    async def evaluate_trigger(
        workspace_id: str,
        trigger_type: str,
        event_data: dict
    ) -> List[dict]:
        """
        Evaluate all rules for a specific trigger.
        Returns list of actions to execute.
        """
        db = get_db()
        
        # Get active rules for this trigger
        rules = await db.automation_rules.find({
            "workspace_id": workspace_id,
            "isActive": True,
            "trigger.type": trigger_type
        }).sort("priority", -1).to_list(length=50)
        
        actions_to_execute = []
        
        for rule in rules:
            # Check conditions
            if CampaignAutomationService._check_conditions(
                rule.get("conditions", []),
                event_data
            ):
                # Add actions with rule context
                for action in rule.get("actions", []):
                    actions_to_execute.append({
                        "ruleId": rule["id"],
                        "ruleName": rule["name"],
                        "action": action,
                        "eventData": event_data
                    })
                
                # Update execution count
                await db.automation_rules.update_one(
                    {"id": rule["id"]},
                    {
                        "$inc": {"executionCount": 1},
                        "$set": {"lastExecuted": datetime.now(timezone.utc).isoformat()}
                    }
                )
        
        return actions_to_execute
    
    @staticmethod
    def _check_conditions(conditions: List[dict], data: dict) -> bool:
        """Check if all conditions are met"""
        if not conditions:
            return True
        
        for condition in conditions:
            field = condition.get("field", "")
            operator = condition.get("operator", "equals")
            expected = condition.get("value")
            
            # Get actual value from data (supports nested fields)
            actual = data
            for key in field.split("."):
                if isinstance(actual, dict):
                    actual = actual.get(key)
                else:
                    actual = None
                    break
            
            # Evaluate condition
            if not CampaignAutomationService._evaluate_condition(
                actual, operator, expected
            ):
                return False
        
        return True
    
    @staticmethod
    def _evaluate_condition(actual: Any, operator: str, expected: Any) -> bool:
        """Evaluate a single condition"""
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "contains":
            return str(expected).lower() in str(actual).lower() if actual else False
        elif operator == "not_contains":
            return str(expected).lower() not in str(actual).lower() if actual else True
        elif operator == "greater_than":
            return float(actual or 0) > float(expected or 0)
        elif operator == "less_than":
            return float(actual or 0) < float(expected or 0)
        elif operator == "greater_or_equal":
            return float(actual or 0) >= float(expected or 0)
        elif operator == "less_or_equal":
            return float(actual or 0) <= float(expected or 0)
        elif operator == "is_empty":
            return not actual
        elif operator == "is_not_empty":
            return bool(actual)
        elif operator == "in_list":
            return actual in (expected if isinstance(expected, list) else [expected])
        elif operator == "not_in_list":
            return actual not in (expected if isinstance(expected, list) else [expected])
        
        return False
    
    @staticmethod
    async def execute_action(
        workspace_id: str,
        action: dict,
        event_data: dict,
        user_id: str
    ) -> dict:
        """Execute an automation action"""
        db = get_db()
        action_type = action.get("type")
        config = action.get("config", {})
        
        result = {"success": False, "action": action_type}
        
        try:
            if action_type == "send_email":
                # Queue email to be sent
                result = await CampaignAutomationService._send_email_action(
                    workspace_id, config, event_data
                )
            
            elif action_type == "create_task":
                result = await CampaignAutomationService._create_task_action(
                    workspace_id, user_id, config, event_data
                )
            
            elif action_type == "update_lead_status":
                result = await CampaignAutomationService._update_lead_status_action(
                    workspace_id, config, event_data
                )
            
            elif action_type == "add_lead_tag":
                result = await CampaignAutomationService._add_lead_tag_action(
                    workspace_id, config, event_data
                )
            
            elif action_type == "schedule_post":
                result = await CampaignAutomationService._schedule_post_action(
                    workspace_id, user_id, config, event_data
                )
            
            elif action_type == "send_notification":
                result = await CampaignAutomationService._send_notification_action(
                    workspace_id, config, event_data
                )
            
            else:
                result = {"success": True, "action": action_type, "status": "acknowledged"}
            
            # Log execution
            await db.automation_logs.insert_one({
                "id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "actionType": action_type,
                "config": config,
                "eventData": event_data,
                "result": result,
                "executedAt": datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            result = {"success": False, "action": action_type, "error": str(e)}
        
        return result
    
    @staticmethod
    async def _send_email_action(workspace_id: str, config: dict, event_data: dict) -> dict:
        """Execute send email action"""
        # Integration with SendGrid would go here
        return {
            "success": True,
            "action": "send_email",
            "recipient": config.get("recipient", event_data.get("email")),
            "template": config.get("template")
        }
    
    @staticmethod
    async def _create_task_action(workspace_id: str, user_id: str, config: dict, event_data: dict) -> dict:
        """Execute create task action"""
        db = get_db()
        
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "workspace_id": workspace_id,
            "title": config.get("title", "Automated Task"),
            "description": config.get("description", f"Auto-created from event: {event_data.get('type', 'unknown')}"),
            "assignee": config.get("assignee", user_id),
            "status": "pending",
            "priority": config.get("priority", "medium"),
            "source": "automation",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        await db.tasks.insert_one(task)
        return {"success": True, "action": "create_task", "taskId": task_id}
    
    @staticmethod
    async def _update_lead_status_action(workspace_id: str, config: dict, event_data: dict) -> dict:
        """Execute update lead status action"""
        db = get_db()
        
        lead_id = event_data.get("lead_id") or config.get("lead_id")
        new_status = config.get("status")
        
        if lead_id and new_status:
            await db.leads.update_one(
                {"id": lead_id, "workspace_id": workspace_id},
                {"$set": {"status": new_status, "updatedAt": datetime.now(timezone.utc).isoformat()}}
            )
            return {"success": True, "action": "update_lead_status", "leadId": lead_id, "status": new_status}
        
        return {"success": False, "action": "update_lead_status", "error": "Missing lead_id or status"}
    
    @staticmethod
    async def _add_lead_tag_action(workspace_id: str, config: dict, event_data: dict) -> dict:
        """Execute add lead tag action"""
        db = get_db()
        
        lead_id = event_data.get("lead_id") or config.get("lead_id")
        tag = config.get("tag")
        
        if lead_id and tag:
            await db.leads.update_one(
                {"id": lead_id, "workspace_id": workspace_id},
                {"$addToSet": {"tags": tag}}
            )
            return {"success": True, "action": "add_lead_tag", "leadId": lead_id, "tag": tag}
        
        return {"success": False, "action": "add_lead_tag", "error": "Missing lead_id or tag"}
    
    @staticmethod
    async def _schedule_post_action(workspace_id: str, user_id: str, config: dict, event_data: dict) -> dict:
        """Execute schedule post action"""
        from app.services.scheduling_service import SchedulingService
        
        action = {
            "type": "social_post",
            "platform": config.get("platform", "linkedin"),
            "content": config.get("content", ""),
            "source": "automation"
        }
        
        result = await SchedulingService.schedule_growth_action(
            workspace_id, user_id, action
        )
        
        return {"success": True, "action": "schedule_post", "scheduledActionId": result.get("id")}
    
    @staticmethod
    async def _send_notification_action(workspace_id: str, config: dict, event_data: dict) -> dict:
        """Execute send notification action"""
        from app.services.websocket_service import RealTimeNotificationService
        
        user_id = config.get("user_id")
        message = config.get("message", "Automation notification")
        
        if user_id:
            await RealTimeNotificationService.notify_user(
                user_id=user_id,
                notification_type="automation",
                title="Automation Alert",
                message=message,
                data={"source": "automation", "eventType": event_data.get("type")},
                workspace_id=workspace_id
            )
            return {"success": True, "action": "send_notification", "userId": user_id}
        
        return {"success": False, "action": "send_notification", "error": "Missing user_id"}
    
    @staticmethod
    async def get_execution_logs(
        workspace_id: str,
        limit: int = 50,
        action_type: Optional[str] = None
    ) -> List[dict]:
        """Get automation execution logs"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if action_type:
            query["actionType"] = action_type
        
        logs = await db.automation_logs.find(query)\
            .sort("executedAt", -1)\
            .limit(limit)\
            .to_list(length=limit)
        
        return [{k: v for k, v in log.items() if k != '_id'} for log in logs]
    
    @staticmethod
    def get_available_triggers() -> dict:
        """Get all available triggers"""
        return CampaignAutomationService.TRIGGERS
    
    @staticmethod
    def get_available_actions() -> dict:
        """Get all available actions"""
        return CampaignAutomationService.ACTIONS
    
    @staticmethod
    def get_available_operators() -> dict:
        """Get all available condition operators"""
        return CampaignAutomationService.OPERATORS
