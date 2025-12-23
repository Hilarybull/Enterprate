"""Finance & Compliance service"""
import uuid
import os
import base64
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.finance import (
    ExpenseCreate, ExpenseUpdate,
    ComplianceChecklistCreate, ComplianceChecklistUpdate,
    TaxEstimateRequest, ReceiptScanRequest
)

# Try to import LLM integration for vision
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageUrl
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class FinanceService:
    """Service for Finance & Compliance operations"""
    
    # UK Tax brackets (simplified)
    UK_TAX_BRACKETS = [
        (12570, 0),      # Personal allowance
        (50270, 0.20),   # Basic rate
        (125140, 0.40),  # Higher rate
        (float('inf'), 0.45)  # Additional rate
    ]
    
    CORPORATION_TAX_RATE = 0.25  # UK corporation tax
    
    # === EXPENSE MANAGEMENT ===
    
    @staticmethod
    async def create_expense(workspace_id: str, user_id: str, data: ExpenseCreate) -> dict:
        """Create a new expense"""
        db = get_db()
        
        expense_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        expense = {
            "id": expense_id,
            "workspace_id": workspace_id,
            "description": data.description,
            "amount": data.amount,
            "category": data.category.value if hasattr(data.category, 'value') else data.category,
            "date": data.date,
            "vendor": data.vendor,
            "receiptUrl": data.receiptUrl,
            "notes": data.notes,
            "status": "pending",  # pending, approved, rejected
            "created_by": user_id,
            "createdAt": now
        }
        
        await db.expenses.insert_one(expense)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "expense.created",
            "data": {"expense_id": expense_id, "amount": data.amount, "category": expense["category"]},
            "occurredAt": now
        })
        
        return {k: v for k, v in expense.items() if k != '_id'}
    
    @staticmethod
    async def get_expenses(workspace_id: str, category: Optional[str] = None) -> List[dict]:
        """Get all expenses for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if category:
            query["category"] = category
        
        expenses = await db.expenses.find(query).sort("date", -1).to_list(length=500)
        
        return [{k: v for k, v in exp.items() if k != '_id'} for exp in expenses]
    
    @staticmethod
    async def update_expense(expense_id: str, workspace_id: str, data: ExpenseUpdate) -> dict:
        """Update an expense"""
        db = get_db()
        
        expense = await db.expenses.find_one({
            "id": expense_id,
            "workspace_id": workspace_id
        })
        
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if "category" in update_data and hasattr(update_data["category"], 'value'):
            update_data["category"] = update_data["category"].value
        
        if update_data:
            await db.expenses.update_one(
                {"id": expense_id},
                {"$set": update_data}
            )
        
        updated = await db.expenses.find_one({"id": expense_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_expense(expense_id: str, workspace_id: str) -> bool:
        """Delete an expense"""
        db = get_db()
        result = await db.expenses.delete_one({
            "id": expense_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def get_expense_summary(workspace_id: str) -> dict:
        """Get expense summary/stats"""
        db = get_db()
        
        expenses = await db.expenses.find({"workspace_id": workspace_id}).to_list(length=1000)
        
        total = sum(e.get("amount", 0) for e in expenses)
        by_category = {}
        by_status = {"pending": 0, "approved": 0, "rejected": 0}
        
        for exp in expenses:
            cat = exp.get("category", "other")
            by_category[cat] = by_category.get(cat, 0) + exp.get("amount", 0)
            status = exp.get("status", "pending")
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "totalExpenses": len(expenses),
            "totalAmount": round(total, 2),
            "byCategory": by_category,
            "byStatus": by_status
        }
    
    # === RECEIPT SCANNING ===
    
    @staticmethod
    async def scan_receipt(workspace_id: str, data: ReceiptScanRequest) -> dict:
        """Scan receipt image and extract data using AI Vision"""
        if not LLM_AVAILABLE:
            return FinanceService._get_mock_receipt_data()
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return FinanceService._get_mock_receipt_data()
            
            # Create chat with vision capability
            chat = LlmChat(
                api_key=llm_key,
                model="gpt-4o",
                system_message="""You are a receipt scanning assistant. Extract information from receipt images.
                Return a JSON object with:
                - vendor: store/business name
                - amount: total amount as a number
                - date: date in YYYY-MM-DD format
                - category: one of: office, travel, marketing, software, utilities, equipment, professional_services, other
                - items: array of {name, quantity, price}
                - confidence: your confidence level 0-1
                
                Return ONLY valid JSON, no markdown formatting."""
            )
            
            # Prepare image
            image_data = data.imageBase64
            if not image_data.startswith("data:"):
                image_data = f"data:image/jpeg;base64,{image_data}"
            
            response = await chat.send_async(
                message=UserMessage(
                    text="Please extract all information from this receipt image.",
                    images=[ImageUrl(url=image_data)]
                )
            )
            
            # Parse response
            import json
            try:
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                
                result = json.loads(text.strip())
                return {
                    "vendor": result.get("vendor"),
                    "amount": result.get("amount"),
                    "date": result.get("date"),
                    "category": result.get("category", "other"),
                    "items": result.get("items", []),
                    "confidence": result.get("confidence", 0.8),
                    "rawText": None
                }
            except:
                return FinanceService._get_mock_receipt_data()
                
        except Exception as e:
            print(f"Receipt scan error: {e}")
            return FinanceService._get_mock_receipt_data()
    
    @staticmethod
    def _get_mock_receipt_data() -> dict:
        """Mock receipt data when AI unavailable"""
        return {
            "vendor": "Example Store",
            "amount": 45.99,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": "office",
            "items": [
                {"name": "Item 1", "quantity": 1, "price": 25.99},
                {"name": "Item 2", "quantity": 2, "price": 10.00}
            ],
            "confidence": 0.0,
            "rawText": "AI scanning unavailable - please enter details manually"
        }
    
    # === TAX ESTIMATION ===
    
    @staticmethod
    async def estimate_tax(workspace_id: str, data: TaxEstimateRequest) -> dict:
        """Estimate tax based on revenue and expenses"""
        taxable_income = data.annualRevenue - data.annualExpenses
        
        if taxable_income <= 0:
            return {
                "estimatedTax": 0,
                "effectiveRate": 0,
                "taxableIncome": 0,
                "breakdown": [],
                "recommendations": ["Your expenses exceed revenue - no tax liability"]
            }
        
        # Calculate based on business type
        if data.businessType == "corporation":
            # Corporation tax
            tax = taxable_income * FinanceService.CORPORATION_TAX_RATE
            breakdown = [
                {"bracket": "Corporation Tax", "rate": "25%", "amount": round(tax, 2)}
            ]
            recommendations = [
                "Consider dividend vs salary mix for tax efficiency",
                "Review allowable business expenses",
                "Plan for quarterly tax payments"
            ]
        else:
            # Income tax (sole proprietor / LLC)
            tax = 0
            breakdown = []
            remaining = taxable_income
            prev_threshold = 0
            
            for threshold, rate in FinanceService.UK_TAX_BRACKETS:
                if remaining <= 0:
                    break
                
                taxable_in_bracket = min(remaining, threshold - prev_threshold)
                tax_in_bracket = taxable_in_bracket * rate
                
                if rate > 0:
                    breakdown.append({
                        "bracket": f"£{prev_threshold:,} - £{threshold:,}" if threshold != float('inf') else f"Above £{prev_threshold:,}",
                        "rate": f"{int(rate * 100)}%",
                        "amount": round(tax_in_bracket, 2)
                    })
                
                tax += tax_in_bracket
                remaining -= taxable_in_bracket
                prev_threshold = threshold
            
            recommendations = [
                "Maximize pension contributions to reduce taxable income",
                "Claim all allowable business expenses",
                "Consider incorporating if profits exceed £50,000",
                "Register for VAT if turnover exceeds £85,000"
            ]
        
        effective_rate = (tax / taxable_income * 100) if taxable_income > 0 else 0
        
        return {
            "estimatedTax": round(tax, 2),
            "effectiveRate": round(effective_rate, 2),
            "taxableIncome": round(taxable_income, 2),
            "breakdown": breakdown,
            "recommendations": recommendations
        }
    
    # === COMPLIANCE CHECKLIST ===
    
    @staticmethod
    async def create_compliance_item(workspace_id: str, user_id: str, data: ComplianceChecklistCreate) -> dict:
        """Create a compliance checklist item"""
        db = get_db()
        
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        item = {
            "id": item_id,
            "workspace_id": workspace_id,
            "title": data.title,
            "description": data.description,
            "category": data.category,
            "dueDate": data.dueDate,
            "priority": data.priority,
            "completed": False,
            "created_by": user_id,
            "createdAt": now
        }
        
        await db.compliance_items.insert_one(item)
        return {k: v for k, v in item.items() if k != '_id'}
    
    @staticmethod
    async def get_compliance_items(workspace_id: str, category: Optional[str] = None) -> List[dict]:
        """Get compliance checklist items"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if category:
            query["category"] = category
        
        items = await db.compliance_items.find(query).sort("dueDate", 1).to_list(length=200)
        return [{k: v for k, v in item.items() if k != '_id'} for item in items]
    
    @staticmethod
    async def update_compliance_item(item_id: str, workspace_id: str, data: ComplianceChecklistUpdate) -> dict:
        """Update a compliance item"""
        db = get_db()
        
        item = await db.compliance_items.find_one({
            "id": item_id,
            "workspace_id": workspace_id
        })
        
        if not item:
            raise HTTPException(status_code=404, detail="Compliance item not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await db.compliance_items.update_one(
                {"id": item_id},
                {"$set": update_data}
            )
        
        updated = await db.compliance_items.find_one({"id": item_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_compliance_item(item_id: str, workspace_id: str) -> bool:
        """Delete a compliance item"""
        db = get_db()
        result = await db.compliance_items.delete_one({
            "id": item_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def get_default_compliance_checklist(business_type: str = "ltd") -> List[dict]:
        """Get default UK compliance checklist"""
        common_items = [
            {
                "title": "Register for Corporation Tax",
                "description": "Register with HMRC within 3 months of starting business",
                "category": "tax",
                "priority": "high"
            },
            {
                "title": "File Confirmation Statement",
                "description": "Annual confirmation statement to Companies House",
                "category": "company",
                "priority": "high"
            },
            {
                "title": "Maintain Company Registers",
                "description": "Keep statutory registers up to date",
                "category": "company",
                "priority": "medium"
            },
            {
                "title": "File Annual Accounts",
                "description": "Submit accounts to Companies House within 9 months of year end",
                "category": "accounts",
                "priority": "high"
            },
            {
                "title": "Corporation Tax Return",
                "description": "File CT600 within 12 months of accounting period end",
                "category": "tax",
                "priority": "high"
            },
            {
                "title": "Register for VAT (if applicable)",
                "description": "Register if turnover exceeds £85,000 threshold",
                "category": "tax",
                "priority": "medium"
            },
            {
                "title": "PAYE Registration",
                "description": "Register as employer if hiring staff",
                "category": "payroll",
                "priority": "medium"
            },
            {
                "title": "Workplace Pension",
                "description": "Set up workplace pension scheme for eligible employees",
                "category": "payroll",
                "priority": "medium"
            },
            {
                "title": "Business Insurance",
                "description": "Arrange appropriate business insurance coverage",
                "category": "insurance",
                "priority": "high"
            },
            {
                "title": "Data Protection Registration",
                "description": "Register with ICO if processing personal data",
                "category": "legal",
                "priority": "medium"
            }
        ]
        
        return common_items
