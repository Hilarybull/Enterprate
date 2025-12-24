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
        import json
        import re
        
        if not LLM_AVAILABLE:
            return FinanceService._get_mock_receipt_data("AI Vision library not available")
        
        try:
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return FinanceService._get_mock_receipt_data("No API key configured")
            
            # Prepare image data - ensure proper format
            image_data = data.imageBase64
            
            # Strip any existing data URL prefix and rebuild
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            
            # Detect image type from base64 header or filename
            image_type = "jpeg"  # default
            if data.filename:
                lower_filename = data.filename.lower()
                if lower_filename.endswith(".png"):
                    image_type = "png"
                elif lower_filename.endswith(".gif"):
                    image_type = "gif"
                elif lower_filename.endswith(".webp"):
                    image_type = "webp"
            
            # Rebuild proper data URL
            full_image_url = f"data:image/{image_type};base64,{image_data}"
            
            # Create chat with vision capability using correct API
            chat = LlmChat(
                api_key=llm_key,
                session_id=f"receipt-scan-{workspace_id}",
                system_message="""You are a receipt scanning assistant. Extract information from receipt images accurately.
                Always return a valid JSON object with these exact fields:
                {
                    "vendor": "store/business name as string",
                    "amount": total amount as number (e.g., 45.99),
                    "date": "date in YYYY-MM-DD format",
                    "category": "one of: office, travel, marketing, software, utilities, equipment, professional_services, other",
                    "items": [{"name": "item name", "quantity": 1, "price": 10.00}],
                    "confidence": 0.8
                }
                
                IMPORTANT: Return ONLY the JSON object, no markdown code blocks, no explanatory text."""
            ).with_model("openai", "gpt-4o")
            
            # Create image content
            from emergentintegrations.llm.chat import ImageContent
            image_content = ImageContent(image_base64=image_data)
            
            response = await chat.send_message(
                UserMessage(
                    text="Please analyze this receipt image and extract: vendor name, total amount, date, expense category, and line items. Return only a JSON object.",
                    file_contents=[image_content]
                )
            )
            
            # Parse response with multiple fallback strategies
            text = response.text.strip()
            
            # Strategy 1: Try to extract JSON from markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Strategy 2: Try to find JSON object pattern
            if not text.startswith("{"):
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
                if json_match:
                    text = json_match.group()
            
            try:
                result = json.loads(text)
                
                # Validate and sanitize the result
                vendor = result.get("vendor") or "Unknown Vendor"
                amount = result.get("amount")
                if isinstance(amount, str):
                    # Remove currency symbols and convert to float
                    amount = float(re.sub(r'[£$€,]', '', amount))
                
                date = result.get("date")
                if not date or not re.match(r'\d{4}-\d{2}-\d{2}', str(date)):
                    date = datetime.now().strftime("%Y-%m-%d")
                
                category = result.get("category", "other")
                valid_categories = ["office", "travel", "marketing", "software", "utilities", "equipment", "professional_services", "other"]
                if category not in valid_categories:
                    category = "other"
                
                items = result.get("items", [])
                if not isinstance(items, list):
                    items = []
                
                confidence = result.get("confidence", 0.8)
                if not isinstance(confidence, (int, float)):
                    confidence = 0.8
                
                return {
                    "vendor": vendor,
                    "amount": amount,
                    "date": date,
                    "category": category,
                    "items": items,
                    "confidence": min(max(float(confidence), 0), 1),  # Clamp between 0-1
                    "rawText": None
                }
                
            except json.JSONDecodeError as je:
                print(f"JSON parsing failed: {je}, text was: {text[:200]}")
                # Try to extract key information with regex as last resort
                extracted = FinanceService._extract_with_regex(text)
                if extracted:
                    return extracted
                return FinanceService._get_mock_receipt_data("Could not parse AI response")
                
        except Exception as e:
            print(f"Receipt scan error: {type(e).__name__}: {e}")
            return FinanceService._get_mock_receipt_data(f"Scan error: {str(e)[:100]}")
    
    @staticmethod
    def _extract_with_regex(text: str) -> dict:
        """Fallback regex extraction from AI text response"""
        import re
        
        result = {
            "vendor": None,
            "amount": None,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": "other",
            "items": [],
            "confidence": 0.5,
            "rawText": text[:500] if text else None
        }
        
        # Try to extract amount
        amount_match = re.search(r'(?:total|amount|£|\$|€)\s*[:=]?\s*([£$€]?\s*[\d,]+\.?\d*)', text, re.IGNORECASE)
        if amount_match:
            amount_str = re.sub(r'[£$€,\s]', '', amount_match.group(1))
            try:
                result["amount"] = float(amount_str)
            except ValueError:
                pass
        
        # Try to extract vendor
        vendor_match = re.search(r'(?:vendor|store|merchant|from)\s*[:=]?\s*["\']?([^"\'\n,]+)', text, re.IGNORECASE)
        if vendor_match:
            result["vendor"] = vendor_match.group(1).strip()
        
        # Try to extract date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if date_match:
            result["date"] = date_match.group(1)
        
        if result["amount"] is not None:
            return result
        return None
    
    @staticmethod
    def _get_mock_receipt_data(reason: str = "AI scanning unavailable") -> dict:
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
            "rawText": f"{reason} - please enter details manually"
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
