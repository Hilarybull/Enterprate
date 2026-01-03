"""Scheduling service for automated growth actions"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from app.core.database import get_db

# Try to import LLM
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class SchedulingService:
    """
    Service for automated scheduling and execution of growth actions.
    Determines optimal posting times based on platform and audience data.
    """
    
    # Default optimal posting times by platform (UK timezone, 24h format)
    OPTIMAL_TIMES = {
        "linkedin": {
            "weekday": ["07:30", "12:00", "17:00"],
            "weekend": ["10:00", "14:00"]
        },
        "twitter": {
            "weekday": ["08:00", "12:00", "17:00", "20:00"],
            "weekend": ["09:00", "15:00", "18:00"]
        },
        "facebook": {
            "weekday": ["09:00", "13:00", "16:00"],
            "weekend": ["12:00", "14:00"]
        },
        "instagram": {
            "weekday": ["07:00", "12:00", "19:00", "21:00"],
            "weekend": ["10:00", "14:00", "20:00"]
        },
        "tiktok": {
            "weekday": ["07:00", "12:00", "19:00", "22:00"],
            "weekend": ["09:00", "12:00", "19:00", "22:00"]
        },
        "youtube": {
            "weekday": ["14:00", "15:00", "16:00"],
            "weekend": ["09:00", "10:00", "11:00"]
        }
    }
    
    # Peak engagement days by platform
    PEAK_DAYS = {
        "linkedin": [1, 2, 3, 4],  # Tue-Fri
        "twitter": [1, 2, 3, 4],   # Tue-Fri
        "facebook": [3, 4, 5],     # Thu-Sat
        "instagram": [0, 1, 2, 6], # Mon-Wed, Sun
        "tiktok": [1, 2, 3, 4, 5, 6],  # Tue-Sun
        "youtube": [3, 4, 5]       # Thu-Sat
    }
    
    @staticmethod
    def get_optimal_schedule(
        platform: str,
        action_type: str = "social_post",
        count: int = 1,
        start_date: Optional[datetime] = None
    ) -> List[dict]:
        """
        Calculate optimal schedule times for a given platform and action type.
        Returns list of scheduled times with engagement predictions.
        """
        if not start_date:
            start_date = datetime.now(timezone.utc)
        
        platform_lower = platform.lower()
        optimal_times = SchedulingService.OPTIMAL_TIMES.get(platform_lower, {})
        peak_days = SchedulingService.PEAK_DAYS.get(platform_lower, [0, 1, 2, 3, 4])
        
        schedules = []
        current_date = start_date
        attempts = 0
        max_attempts = count * 7  # Don't look more than 7 days per post
        
        while len(schedules) < count and attempts < max_attempts:
            day_of_week = current_date.weekday()  # 0=Mon, 6=Sun
            is_weekend = day_of_week >= 5
            
            time_slots = optimal_times.get("weekend" if is_weekend else "weekday", ["12:00"])
            is_peak_day = day_of_week in peak_days
            
            for time_str in time_slots:
                if len(schedules) >= count:
                    break
                
                hour, minute = map(int, time_str.split(":"))
                scheduled_time = current_date.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                
                # Skip if in the past
                if scheduled_time <= datetime.now(timezone.utc):
                    continue
                
                # Calculate engagement score
                engagement_score = SchedulingService._calculate_engagement_score(
                    platform_lower, day_of_week, hour, is_peak_day
                )
                
                schedules.append({
                    "scheduledFor": scheduled_time.isoformat(),
                    "platform": platform,
                    "timeSlot": time_str,
                    "dayOfWeek": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day_of_week],
                    "isPeakDay": is_peak_day,
                    "isWeekend": is_weekend,
                    "predictedEngagement": engagement_score,
                    "recommendation": "High" if engagement_score > 75 else "Medium" if engagement_score > 50 else "Low"
                })
            
            current_date += timedelta(days=1)
            attempts += 1
        
        # Sort by engagement score
        schedules.sort(key=lambda x: x["predictedEngagement"], reverse=True)
        return schedules[:count]
    
    @staticmethod
    def _calculate_engagement_score(platform: str, day_of_week: int, hour: int, is_peak_day: bool) -> int:
        """Calculate predicted engagement score (0-100)"""
        base_score = 50
        
        # Peak day bonus
        if is_peak_day:
            base_score += 20
        
        # Time-based scoring
        if platform == "linkedin":
            # Best times: 7-8am, 12pm, 5pm
            if hour in [7, 8, 12, 17]:
                base_score += 15
            elif hour in [9, 10, 11, 16]:
                base_score += 10
        elif platform == "twitter":
            # Best times: 8am, 12pm, 5pm, 8pm
            if hour in [8, 12, 17, 20]:
                base_score += 15
            elif hour in [9, 13, 18, 19]:
                base_score += 10
        elif platform == "instagram":
            # Best times: 7am, 12pm, 7pm, 9pm
            if hour in [7, 12, 19, 21]:
                base_score += 15
            elif hour in [11, 13, 18, 20]:
                base_score += 10
        elif platform == "facebook":
            # Best times: 9am, 1pm, 4pm
            if hour in [9, 13, 16]:
                base_score += 15
            elif hour in [10, 12, 14, 15]:
                base_score += 10
        
        # Weekend penalty for B2B platforms
        if platform == "linkedin" and day_of_week >= 5:
            base_score -= 15
        
        return min(100, max(0, base_score))
    
    @staticmethod
    async def schedule_growth_action(
        workspace_id: str,
        user_id: str,
        action: dict,
        schedule_config: Optional[dict] = None
    ) -> dict:
        """
        Schedule a growth action for automatic execution.
        Can be immediately or at optimal times.
        """
        db = get_db()
        
        action_type = action.get("type", "social_post")
        platform = action.get("platform", "linkedin")
        
        # Get optimal schedule if not specified
        if schedule_config and schedule_config.get("scheduledFor"):
            scheduled_for = schedule_config["scheduledFor"]
        else:
            optimal = SchedulingService.get_optimal_schedule(platform, action_type, 1)
            scheduled_for = optimal[0]["scheduledFor"] if optimal else datetime.now(timezone.utc).isoformat()
        
        # Create scheduled action
        action_id = str(uuid.uuid4())
        scheduled_action = {
            "id": action_id,
            "workspace_id": workspace_id,
            "actionType": action_type,
            "platform": platform,
            "content": action.get("content"),
            "hashtags": action.get("hashtags", []),
            "scheduledFor": scheduled_for,
            "status": "scheduled",  # scheduled, executed, failed, cancelled
            "source": action.get("source", "growth_agent"),
            "recommendationId": action.get("recommendationId"),
            "createdBy": user_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "executedAt": None,
            "error": None
        }
        
        await db.scheduled_actions.insert_one(scheduled_action)
        
        return {k: v for k, v in scheduled_action.items() if k != '_id'}
    
    @staticmethod
    async def get_scheduled_actions(
        workspace_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[dict]:
        """Get scheduled actions for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if status:
            query["status"] = status
        if platform:
            query["platform"] = platform
        
        actions = await db.scheduled_actions.find(query).sort("scheduledFor", 1).to_list(length=100)
        return [{k: v for k, v in a.items() if k != '_id'} for a in actions]
    
    @staticmethod
    async def execute_scheduled_action(action_id: str, workspace_id: str) -> dict:
        """Execute a scheduled action (creates the social post)"""
        db = get_db()
        
        action = await db.scheduled_actions.find_one({
            "id": action_id,
            "workspace_id": workspace_id
        })
        
        if not action:
            return {"success": False, "error": "Action not found"}
        
        if action.get("status") != "scheduled":
            return {"success": False, "error": f"Action already {action.get('status')}"}
        
        try:
            # Create the social post
            post_id = str(uuid.uuid4())
            post = {
                "id": post_id,
                "workspace_id": workspace_id,
                "platform": action.get("platform"),
                "content": action.get("content"),
                "hashtags": action.get("hashtags", []),
                "status": "published",
                "scheduledFor": action.get("scheduledFor"),
                "postedAt": datetime.now(timezone.utc).isoformat(),
                "source": action.get("source", "growth_agent"),
                "createdBy": action.get("createdBy"),
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
            
            await db.social_posts.insert_one(post)
            
            # Update scheduled action
            await db.scheduled_actions.update_one(
                {"id": action_id},
                {
                    "$set": {
                        "status": "executed",
                        "executedAt": datetime.now(timezone.utc).isoformat(),
                        "resultPostId": post_id
                    }
                }
            )
            
            return {
                "success": True,
                "postId": post_id,
                "executedAt": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            # Mark as failed
            await db.scheduled_actions.update_one(
                {"id": action_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e)
                    }
                }
            )
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def cancel_scheduled_action(action_id: str, workspace_id: str) -> bool:
        """Cancel a scheduled action"""
        db = get_db()
        
        result = await db.scheduled_actions.update_one(
            {
                "id": action_id,
                "workspace_id": workspace_id,
                "status": "scheduled"
            },
            {"$set": {"status": "cancelled"}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def process_due_actions():
        """Process all due scheduled actions (for background job)"""
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()
        
        due_actions = await db.scheduled_actions.find({
            "status": "scheduled",
            "scheduledFor": {"$lte": now}
        }).to_list(length=100)
        
        results = []
        for action in due_actions:
            result = await SchedulingService.execute_scheduled_action(
                action["id"],
                action["workspace_id"]
            )
            results.append({
                "actionId": action["id"],
                **result
            })
        
        return results
    
    @staticmethod
    async def get_schedule_analytics(workspace_id: str) -> dict:
        """Get analytics about scheduled actions"""
        db = get_db()
        
        all_actions = await db.scheduled_actions.find({
            "workspace_id": workspace_id
        }).to_list(length=500)
        
        total = len(all_actions)
        by_status = {"scheduled": 0, "executed": 0, "failed": 0, "cancelled": 0}
        by_platform = {}
        
        for action in all_actions:
            status = action.get("status", "scheduled")
            platform = action.get("platform", "other")
            
            by_status[status] = by_status.get(status, 0) + 1
            by_platform[platform] = by_platform.get(platform, 0) + 1
        
        success_rate = (by_status["executed"] / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "byStatus": by_status,
            "byPlatform": by_platform,
            "successRate": round(success_rate, 1),
            "pending": by_status["scheduled"]
        }
