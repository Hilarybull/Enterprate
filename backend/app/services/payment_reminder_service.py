"""Invoice Payment Reminder Service - Automated payment tracking and reminders"""
import os
import base64
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.core.database import get_db
from app.services.intelligence_service import log_invoice_event

# SendGrid for email
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    SENDGRID_KEY = os.environ.get("SENDGRID_API_KEY")
    SENDGRID_FROM = os.environ.get("SENDGRID_FROM_EMAIL", "REPLACE_WITH_YOUR_VERIFIED_EMAIL@yourdomain.com")
    SENDGRID_AVAILABLE = bool(SENDGRID_KEY) and not SENDGRID_FROM.startswith("REPLACE_")
except ImportError:
    SENDGRID_AVAILABLE = False
    SENDGRID_KEY = None
    SENDGRID_FROM = None


class PaymentReminderService:
    """Service for tracking invoice payments and sending reminders"""
    
    # Reminder schedule: days relative to due date (negative = before, positive = after)
    REMINDER_SCHEDULE = {
        "before_due": -3,      # 3 days before due date
        "on_due_date": 0,      # On due date
        "first_overdue": 7,    # 7 days after due date
        "second_overdue": 14,  # 14 days after (escalation)
        "final_notice": 30     # 30 days after (final notice)
    }
    
    @staticmethod
    async def check_and_update_overdue_invoices(workspace_id: str = None) -> dict:
        """Check all invoices and mark overdue ones"""
        db = get_db()
        
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        query = {"status": "sent"}
        if workspace_id:
            query["workspace_id"] = workspace_id
        
        # Find sent invoices with past due dates
        invoices = await db.invoices.find(query).to_list(length=1000)
        
        updated_count = 0
        for invoice in invoices:
            due_date = invoice.get("dueDate")
            if due_date and due_date < today:
                await db.invoices.update_one(
                    {"id": invoice["id"]},
                    {"$set": {"status": "overdue", "updatedAt": datetime.now(timezone.utc).isoformat()}}
                )
                updated_count += 1
        
        return {"checked": len(invoices), "marked_overdue": updated_count}
    
    @staticmethod
    async def get_invoices_needing_reminders(workspace_id: str = None) -> List[dict]:
        """Get invoices that need payment reminders"""
        db = get_db()
        
        today = datetime.now(timezone.utc).date()
        
        query = {"status": {"$in": ["sent", "overdue"]}}
        if workspace_id:
            query["workspace_id"] = workspace_id
        
        invoices = await db.invoices.find(query).to_list(length=1000)
        
        reminders_needed = []
        
        for invoice in invoices:
            due_date_str = invoice.get("dueDate")
            if not due_date_str:
                continue
            
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            days_until_due = (due_date - today).days
            last_reminder = invoice.get("lastReminderSent")
            last_reminder_type = invoice.get("lastReminderType")
            
            # Determine which reminder to send
            reminder_type = None
            
            if days_until_due == PaymentReminderService.REMINDER_SCHEDULE["before_due"]:
                if last_reminder_type != "before_due":
                    reminder_type = "before_due"
            elif days_until_due == PaymentReminderService.REMINDER_SCHEDULE["on_due_date"]:
                if last_reminder_type not in ["before_due", "on_due_date"]:
                    reminder_type = "on_due_date"
            elif days_until_due <= -PaymentReminderService.REMINDER_SCHEDULE["first_overdue"]:
                if last_reminder_type not in ["first_overdue", "second_overdue", "final_notice"]:
                    reminder_type = "first_overdue"
            elif days_until_due <= -PaymentReminderService.REMINDER_SCHEDULE["second_overdue"]:
                if last_reminder_type not in ["second_overdue", "final_notice"]:
                    reminder_type = "second_overdue"
            elif days_until_due <= -PaymentReminderService.REMINDER_SCHEDULE["final_notice"]:
                if last_reminder_type != "final_notice":
                    reminder_type = "final_notice"
            
            if reminder_type:
                reminders_needed.append({
                    "invoice": {k: v for k, v in invoice.items() if k != '_id'},
                    "reminder_type": reminder_type,
                    "days_until_due": days_until_due
                })
        
        return reminders_needed
    
    @staticmethod
    async def send_payment_reminder(invoice_id: str, workspace_id: str, reminder_type: str) -> dict:
        """Send a payment reminder email for an invoice"""
        if not SENDGRID_AVAILABLE:
            return {"success": False, "error": "Email service not configured. Please set SENDGRID_FROM_EMAIL to a verified sender."}
        
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            return {"success": False, "error": "Invoice not found"}
        
        # Get workspace for company name
        workspace = await db.workspaces.find_one({"id": workspace_id})
        company_name = workspace.get("name", "Your Business") if workspace else "Your Business"
        
        # Build email content based on reminder type
        currency_symbol = "£" if invoice.get("currency") == "GBP" else "$" if invoice.get("currency") == "USD" else "€"
        amount_due = f"{currency_symbol}{invoice.get('total', 0):.2f}"
        
        email_templates = {
            "before_due": {
                "subject": f"Friendly Reminder: Invoice {invoice.get('invoiceNumber')} Due Soon",
                "heading": "Payment Reminder",
                "message": f"This is a friendly reminder that your invoice is due in 3 days.",
                "urgency": "low"
            },
            "on_due_date": {
                "subject": f"Invoice {invoice.get('invoiceNumber')} is Due Today",
                "heading": "Payment Due Today",
                "message": f"Your invoice is due today. Please arrange payment at your earliest convenience.",
                "urgency": "medium"
            },
            "first_overdue": {
                "subject": f"Overdue: Invoice {invoice.get('invoiceNumber')} - Payment Required",
                "heading": "Payment Overdue",
                "message": f"Your invoice is now 7 days overdue. Please arrange immediate payment to avoid any service interruptions.",
                "urgency": "high"
            },
            "second_overdue": {
                "subject": f"Urgent: Invoice {invoice.get('invoiceNumber')} - 14 Days Overdue",
                "heading": "Urgent: Payment Required",
                "message": f"Your invoice is now 14 days overdue. Please contact us immediately to discuss payment arrangements.",
                "urgency": "high"
            },
            "final_notice": {
                "subject": f"Final Notice: Invoice {invoice.get('invoiceNumber')} - Immediate Action Required",
                "heading": "Final Payment Notice",
                "message": f"This is a final notice. Your invoice is 30+ days overdue. Failure to pay may result in further action.",
                "urgency": "critical"
            }
        }
        
        template = email_templates.get(reminder_type, email_templates["first_overdue"])
        
        urgency_colors = {
            "low": "#4F46E5",      # Indigo
            "medium": "#F59E0B",   # Amber
            "high": "#EF4444",     # Red
            "critical": "#991B1B"  # Dark Red
        }
        
        color = urgency_colors.get(template["urgency"], "#4F46E5")
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background: {color}; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">{template['heading']}</h1>
            </div>
            
            <div style="padding: 30px; background: #f9fafb;">
                <p>Dear {invoice.get('clientName')},</p>
                
                <p>{template['message']}</p>
                
                <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid {color};">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Invoice Number:</td>
                            <td style="padding: 8px 0; text-align: right;">{invoice.get('invoiceNumber')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Amount Due:</td>
                            <td style="padding: 8px 0; text-align: right; font-size: 24px; color: {color};">{amount_due}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Due Date:</td>
                            <td style="padding: 8px 0; text-align: right;">{invoice.get('dueDate', 'Upon receipt')}</td>
                        </tr>
                    </table>
                </div>
                
                <p>If you have already made this payment, please disregard this reminder and accept our thanks.</p>
                
                <p>If you have any questions or need to discuss payment arrangements, please don't hesitate to contact us.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>{company_name}</strong>
                </p>
            </div>
            
            <div style="background: #374151; color: #9CA3AF; padding: 15px; text-align: center; font-size: 12px;">
                This is an automated reminder from {company_name}
            </div>
        </body>
        </html>
        """
        
        try:
            message = Mail(
                from_email=SENDGRID_FROM,
                to_emails=invoice.get("clientEmail"),
                subject=template["subject"],
                html_content=html_content
            )
            
            sg = SendGridAPIClient(SENDGRID_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 202]:
                # Update invoice with reminder info
                now = datetime.now(timezone.utc).isoformat()
                
                reminder_history = invoice.get("reminderHistory", [])
                reminder_history.append({
                    "type": reminder_type,
                    "sentAt": now,
                    "recipient": invoice.get("clientEmail")
                })
                
                await db.invoices.update_one(
                    {"id": invoice_id},
                    {"$set": {
                        "lastReminderSent": now,
                        "lastReminderType": reminder_type,
                        "reminderHistory": reminder_history,
                        "updatedAt": now
                    }}
                )
                
                # Log intelligence event
                await log_invoice_event(
                    workspace_id=workspace_id,
                    user_id="system",
                    event_type="reminder_sent",
                    invoice_id=invoice_id,
                    data={
                        "invoiceNumber": invoice.get("invoiceNumber"),
                        "reminderType": reminder_type,
                        "recipient": invoice.get("clientEmail")
                    }
                )
                
                return {"success": True, "message": f"Reminder ({reminder_type}) sent successfully"}
            else:
                return {"success": False, "error": f"Failed to send email: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def mark_invoice_paid(invoice_id: str, workspace_id: str, user_id: str, payment_date: str = None, payment_method: str = None) -> dict:
        """Mark an invoice as paid"""
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            return {"success": False, "error": "Invoice not found"}
        
        now = datetime.now(timezone.utc).isoformat()
        
        update_data = {
            "status": "paid",
            "paidAt": payment_date or now[:10],
            "paymentMethod": payment_method,
            "updatedAt": now
        }
        
        await db.invoices.update_one(
            {"id": invoice_id},
            {"$set": update_data}
        )
        
        # Log intelligence event
        await log_invoice_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type="paid",
            invoice_id=invoice_id,
            data={
                "invoiceNumber": invoice.get("invoiceNumber"),
                "total": invoice.get("total"),
                "paymentMethod": payment_method
            }
        )
        
        updated = await db.invoices.find_one({"id": invoice_id})
        return {"success": True, "invoice": {k: v for k, v in updated.items() if k != '_id'}}
    
    @staticmethod
    async def get_payment_summary(workspace_id: str) -> dict:
        """Get payment status summary for dashboard"""
        db = get_db()
        
        pipeline = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total": {"$sum": "$total"}
            }}
        ]
        
        results = await db.invoices.aggregate(pipeline).to_list(length=20)
        
        summary = {
            "draft": {"count": 0, "total": 0},
            "pending_review": {"count": 0, "total": 0},
            "sent": {"count": 0, "total": 0},
            "paid": {"count": 0, "total": 0},
            "overdue": {"count": 0, "total": 0}
        }
        
        for r in results:
            status = r["_id"]
            if status in summary:
                summary[status] = {"count": r["count"], "total": round(r["total"], 2)}
        
        # Calculate totals
        total_outstanding = summary["sent"]["total"] + summary["overdue"]["total"]
        total_collected = summary["paid"]["total"]
        
        return {
            "byStatus": summary,
            "totalOutstanding": total_outstanding,
            "totalCollected": total_collected,
            "overdueCount": summary["overdue"]["count"],
            "overdueAmount": summary["overdue"]["total"]
        }
    
    @staticmethod
    async def process_all_reminders(workspace_id: str = None) -> dict:
        """Process and send all due reminders"""
        # First update overdue status
        await PaymentReminderService.check_and_update_overdue_invoices(workspace_id)
        
        # Get invoices needing reminders
        reminders = await PaymentReminderService.get_invoices_needing_reminders(workspace_id)
        
        sent = 0
        failed = 0
        errors = []
        
        for reminder in reminders:
            invoice = reminder["invoice"]
            result = await PaymentReminderService.send_payment_reminder(
                invoice["id"],
                invoice["workspace_id"],
                reminder["reminder_type"]
            )
            
            if result.get("success"):
                sent += 1
            else:
                failed += 1
                errors.append({
                    "invoiceNumber": invoice.get("invoiceNumber"),
                    "error": result.get("error")
                })
        
        return {
            "processed": len(reminders),
            "sent": sent,
            "failed": failed,
            "errors": errors if errors else None
        }
