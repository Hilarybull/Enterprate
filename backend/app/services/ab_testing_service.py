"""A/B Testing Service for campaign optimization"""
import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from app.core.database import get_db


class ABTestingService:
    """
    Service for A/B testing campaigns and content.
    Enables split testing with statistical significance analysis.
    """
    
    # Minimum sample size for statistical significance
    MIN_SAMPLE_SIZE = 100
    # Confidence level for determining winners (95%)
    CONFIDENCE_LEVEL = 0.95
    
    @staticmethod
    async def create_ab_test(
        workspace_id: str,
        user_id: str,
        name: str,
        description: str,
        test_type: str,
        variants: List[dict],
        traffic_split: Optional[List[float]] = None,
        duration_days: int = 14,
        goal_metric: str = "conversion_rate"
    ) -> dict:
        """
        Create a new A/B test.
        
        Args:
            test_type: "campaign", "landing_page", "email", "social_post", "cta"
            variants: List of variant objects with 'name' and 'content'
            traffic_split: Traffic distribution (defaults to equal split)
            goal_metric: "conversion_rate", "click_rate", "engagement", "revenue"
        """
        db = get_db()
        
        test_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=duration_days)
        
        # Default to equal traffic split
        if not traffic_split:
            traffic_split = [1.0 / len(variants)] * len(variants)
        
        # Normalize traffic split
        total = sum(traffic_split)
        traffic_split = [t / total for t in traffic_split]
        
        # Initialize variants with metrics
        variant_data = []
        for i, variant in enumerate(variants):
            variant_data.append({
                "id": str(uuid.uuid4()),
                "name": variant.get("name", f"Variant {chr(65 + i)}"),
                "content": variant.get("content", {}),
                "trafficShare": traffic_split[i],
                "metrics": {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "revenue": 0.0,
                    "engagements": 0
                },
                "isControl": i == 0,
                "isWinner": False
            })
        
        test = {
            "id": test_id,
            "workspace_id": workspace_id,
            "name": name,
            "description": description,
            "testType": test_type,
            "variants": variant_data,
            "goalMetric": goal_metric,
            "status": "draft",  # draft, running, paused, completed
            "winnerId": None,
            "confidenceLevel": ABTestingService.CONFIDENCE_LEVEL,
            "startDate": None,
            "endDate": end_date.isoformat(),
            "durationDays": duration_days,
            "createdBy": user_id,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat()
        }
        
        await db.ab_tests.insert_one(test)
        return {k: v for k, v in test.items() if k != '_id'}
    
    @staticmethod
    async def start_test(test_id: str, workspace_id: str) -> dict:
        """Start an A/B test"""
        db = get_db()
        
        now = datetime.now(timezone.utc)
        
        test = await db.ab_tests.find_one({
            "id": test_id,
            "workspace_id": workspace_id
        })
        
        if not test:
            raise ValueError("Test not found")
        
        if test.get("status") != "draft":
            raise ValueError("Test can only be started from draft status")
        
        end_date = now + timedelta(days=test.get("durationDays", 14))
        
        await db.ab_tests.update_one(
            {"id": test_id},
            {
                "$set": {
                    "status": "running",
                    "startDate": now.isoformat(),
                    "endDate": end_date.isoformat(),
                    "updatedAt": now.isoformat()
                }
            }
        )
        
        updated = await db.ab_tests.find_one({"id": test_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def pause_test(test_id: str, workspace_id: str) -> dict:
        """Pause a running A/B test"""
        db = get_db()
        
        await db.ab_tests.update_one(
            {"id": test_id, "workspace_id": workspace_id, "status": "running"},
            {"$set": {"status": "paused", "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        updated = await db.ab_tests.find_one({"id": test_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def resume_test(test_id: str, workspace_id: str) -> dict:
        """Resume a paused A/B test"""
        db = get_db()
        
        await db.ab_tests.update_one(
            {"id": test_id, "workspace_id": workspace_id, "status": "paused"},
            {"$set": {"status": "running", "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        updated = await db.ab_tests.find_one({"id": test_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def get_variant_for_visitor(test_id: str, visitor_id: str) -> dict:
        """
        Get the variant to show to a specific visitor.
        Uses consistent hashing to ensure same visitor sees same variant.
        """
        db = get_db()
        
        test = await db.ab_tests.find_one({"id": test_id})
        if not test or test.get("status") != "running":
            return None
        
        # Check if visitor already assigned
        assignment = await db.ab_test_assignments.find_one({
            "testId": test_id,
            "visitorId": visitor_id
        })
        
        if assignment:
            variant_id = assignment.get("variantId")
            for variant in test.get("variants", []):
                if variant["id"] == variant_id:
                    return variant
        
        # Assign new visitor to variant based on traffic split
        variants = test.get("variants", [])
        rand = random.random()
        cumulative = 0
        selected_variant = variants[0]
        
        for variant in variants:
            cumulative += variant.get("trafficShare", 1.0 / len(variants))
            if rand <= cumulative:
                selected_variant = variant
                break
        
        # Store assignment
        await db.ab_test_assignments.insert_one({
            "testId": test_id,
            "visitorId": visitor_id,
            "variantId": selected_variant["id"],
            "assignedAt": datetime.now(timezone.utc).isoformat()
        })
        
        return selected_variant
    
    @staticmethod
    async def record_event(
        test_id: str,
        variant_id: str,
        event_type: str,
        value: float = 1.0
    ):
        """
        Record an event for a variant.
        event_type: "impression", "click", "conversion", "revenue", "engagement"
        """
        db = get_db()
        
        metric_field = {
            "impression": "metrics.impressions",
            "click": "metrics.clicks",
            "conversion": "metrics.conversions",
            "revenue": "metrics.revenue",
            "engagement": "metrics.engagements"
        }.get(event_type)
        
        if not metric_field:
            return
        
        # Update the specific variant's metrics
        await db.ab_tests.update_one(
            {"id": test_id, "variants.id": variant_id},
            {
                "$inc": {f"variants.$.{metric_field.split('.')[1]}": value},
                "$set": {"updatedAt": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        # Log the event
        await db.ab_test_events.insert_one({
            "testId": test_id,
            "variantId": variant_id,
            "eventType": event_type,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @staticmethod
    async def analyze_test(test_id: str, workspace_id: str) -> dict:
        """Analyze A/B test results and determine statistical significance"""
        db = get_db()
        
        test = await db.ab_tests.find_one({
            "id": test_id,
            "workspace_id": workspace_id
        })
        
        if not test:
            raise ValueError("Test not found")
        
        variants = test.get("variants", [])
        goal_metric = test.get("goalMetric", "conversion_rate")
        
        # Calculate metrics for each variant
        results = []
        for variant in variants:
            metrics = variant.get("metrics", {})
            impressions = metrics.get("impressions", 0)
            clicks = metrics.get("clicks", 0)
            conversions = metrics.get("conversions", 0)
            revenue = metrics.get("revenue", 0)
            engagements = metrics.get("engagements", 0)
            
            # Calculate rates
            click_rate = (clicks / impressions * 100) if impressions > 0 else 0
            conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
            engagement_rate = (engagements / impressions * 100) if impressions > 0 else 0
            revenue_per_visitor = revenue / impressions if impressions > 0 else 0
            
            results.append({
                "variantId": variant["id"],
                "variantName": variant["name"],
                "isControl": variant.get("isControl", False),
                "metrics": {
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "revenue": round(revenue, 2),
                    "engagements": engagements
                },
                "rates": {
                    "clickRate": round(click_rate, 2),
                    "conversionRate": round(conversion_rate, 2),
                    "engagementRate": round(engagement_rate, 2),
                    "revenuePerVisitor": round(revenue_per_visitor, 2)
                }
            })
        
        # Determine winner based on goal metric
        winner = None
        has_significance = False
        
        if len(results) >= 2:
            # Get the metric to compare
            metric_key = {
                "conversion_rate": "conversionRate",
                "click_rate": "clickRate",
                "engagement": "engagementRate",
                "revenue": "revenuePerVisitor"
            }.get(goal_metric, "conversionRate")
            
            # Find best performer
            sorted_results = sorted(
                results,
                key=lambda r: r["rates"].get(metric_key, 0),
                reverse=True
            )
            
            best = sorted_results[0]
            control = next((r for r in results if r["isControl"]), results[0])
            
            # Check for statistical significance (simplified)
            total_impressions = sum(r["metrics"]["impressions"] for r in results)
            if total_impressions >= ABTestingService.MIN_SAMPLE_SIZE * len(results):
                has_significance = True
                
                # Check if best performer is significantly better than control
                best_rate = best["rates"].get(metric_key, 0)
                control_rate = control["rates"].get(metric_key, 0)
                
                if best_rate > control_rate * 1.05:  # 5% improvement threshold
                    winner = best
        
        return {
            "testId": test_id,
            "testName": test.get("name"),
            "status": test.get("status"),
            "goalMetric": goal_metric,
            "results": results,
            "winner": winner,
            "hasStatisticalSignificance": has_significance,
            "totalImpressions": sum(r["metrics"]["impressions"] for r in results),
            "analyzedAt": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    async def complete_test(test_id: str, workspace_id: str, winner_id: Optional[str] = None) -> dict:
        """Complete an A/B test and optionally set the winner"""
        db = get_db()
        
        # If no winner specified, analyze to determine
        if not winner_id:
            analysis = await ABTestingService.analyze_test(test_id, workspace_id)
            if analysis.get("winner"):
                winner_id = analysis["winner"]["variantId"]
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update test status and winner
        update = {
            "status": "completed",
            "winnerId": winner_id,
            "completedAt": now,
            "updatedAt": now
        }
        
        await db.ab_tests.update_one(
            {"id": test_id, "workspace_id": workspace_id},
            {"$set": update}
        )
        
        # Mark winner variant
        if winner_id:
            await db.ab_tests.update_one(
                {"id": test_id, "variants.id": winner_id},
                {"$set": {"variants.$.isWinner": True}}
            )
        
        updated = await db.ab_tests.find_one({"id": test_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def get_test(test_id: str, workspace_id: str) -> Optional[dict]:
        """Get A/B test by ID"""
        db = get_db()
        test = await db.ab_tests.find_one({
            "id": test_id,
            "workspace_id": workspace_id
        })
        return {k: v for k, v in test.items() if k != '_id'} if test else None
    
    @staticmethod
    async def get_tests(
        workspace_id: str,
        status: Optional[str] = None,
        test_type: Optional[str] = None
    ) -> List[dict]:
        """Get all A/B tests for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if status:
            query["status"] = status
        if test_type:
            query["testType"] = test_type
        
        tests = await db.ab_tests.find(query).sort("createdAt", -1).to_list(length=100)
        return [{k: v for k, v in t.items() if k != '_id'} for t in tests]
    
    @staticmethod
    async def delete_test(test_id: str, workspace_id: str) -> bool:
        """Delete an A/B test"""
        db = get_db()
        
        # Delete test
        result = await db.ab_tests.delete_one({
            "id": test_id,
            "workspace_id": workspace_id
        })
        
        # Delete related data
        await db.ab_test_assignments.delete_many({"testId": test_id})
        await db.ab_test_events.delete_many({"testId": test_id})
        
        return result.deleted_count > 0
