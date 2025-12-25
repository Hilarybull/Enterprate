"""Operations service - Tasks, Email, Documents, Workflows"""
import uuid
import os
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.operations import (
    TaskCreate, TaskUpdate, TaskStatus,
    EmailTemplateCreate, EmailTemplateUpdate, EmailSendRequest,
    DocumentCreate, DocumentUpdate,
    WorkflowTemplateCreate, WorkflowStep
)


class OperationsService:
    """Service for Operations - Tasks, Email, Documents, Workflows"""
    
    # === TASK MANAGEMENT ===
    
    @staticmethod
    async def create_task(workspace_id: str, user_id: str, data: TaskCreate) -> dict:
        """Create a new task"""
        db = get_db()
        
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        task = {
            "id": task_id,
            "workspace_id": workspace_id,
            "title": data.title,
            "description": data.description,
            "status": "todo",
            "priority": data.priority.value if hasattr(data.priority, 'value') else data.priority,
            "dueDate": data.dueDate,
            "assignee": data.assignee,
            "projectId": data.projectId,
            "tags": data.tags,
            "created_by": user_id,
            "createdAt": now,
            "completedAt": None
        }
        
        await db.tasks.insert_one(task)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "task.created",
            "data": {"task_id": task_id, "title": data.title},
            "occurredAt": now
        })
        
        return {k: v for k, v in task.items() if k != '_id'}
    
    @staticmethod
    async def get_tasks(workspace_id: str, status: Optional[str] = None, project_id: Optional[str] = None) -> List[dict]:
        """Get tasks for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if status:
            query["status"] = status
        if project_id:
            query["projectId"] = project_id
        
        tasks = await db.tasks.find(query).sort("createdAt", -1).to_list(length=500)
        return [{k: v for k, v in task.items() if k != '_id'} for task in tasks]
    
    @staticmethod
    async def update_task(task_id: str, workspace_id: str, data: TaskUpdate) -> dict:
        """Update a task"""
        db = get_db()
        
        task = await db.tasks.find_one({
            "id": task_id,
            "workspace_id": workspace_id
        })
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle enum values
        if "status" in update_data and hasattr(update_data["status"], 'value'):
            update_data["status"] = update_data["status"].value
        if "priority" in update_data and hasattr(update_data["priority"], 'value'):
            update_data["priority"] = update_data["priority"].value
        
        # Set completedAt if status changed to completed
        if update_data.get("status") == "completed":
            update_data["completedAt"] = datetime.now(timezone.utc).isoformat()
        
        if update_data:
            await db.tasks.update_one(
                {"id": task_id},
                {"$set": update_data}
            )
        
        updated = await db.tasks.find_one({"id": task_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_task(task_id: str, workspace_id: str) -> bool:
        """Delete a task"""
        db = get_db()
        result = await db.tasks.delete_one({
            "id": task_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def get_task_stats(workspace_id: str) -> dict:
        """Get task statistics"""
        db = get_db()
        
        tasks = await db.tasks.find({"workspace_id": workspace_id}).to_list(length=1000)
        
        by_status = {"todo": 0, "in_progress": 0, "review": 0, "completed": 0, "cancelled": 0}
        by_priority = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
        
        for task in tasks:
            status = task.get("status", "todo")
            priority = task.get("priority", "medium")
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total": len(tasks),
            "byStatus": by_status,
            "byPriority": by_priority,
            "completionRate": round((by_status["completed"] / len(tasks) * 100) if tasks else 0, 1)
        }
    
    # === EMAIL AUTOMATION (MOCKED - SendGrid placeholder) ===
    
    @staticmethod
    async def create_email_template(workspace_id: str, user_id: str, data: EmailTemplateCreate) -> dict:
        """Create email template"""
        db = get_db()
        
        template_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        template = {
            "id": template_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "subject": data.subject,
            "bodyHtml": data.bodyHtml,
            "bodyText": data.bodyText,
            "category": data.category,
            "created_by": user_id,
            "createdAt": now
        }
        
        await db.email_templates.insert_one(template)
        return {k: v for k, v in template.items() if k != '_id'}
    
    @staticmethod
    async def get_email_templates(workspace_id: str) -> List[dict]:
        """Get all email templates"""
        db = get_db()
        
        templates = await db.email_templates.find(
            {"workspace_id": workspace_id}
        ).sort("createdAt", -1).to_list(length=100)
        
        return [{k: v for k, v in t.items() if k != '_id'} for t in templates]
    
    @staticmethod
    async def update_email_template(template_id: str, workspace_id: str, data: EmailTemplateUpdate) -> dict:
        """Update email template"""
        db = get_db()
        
        template = await db.email_templates.find_one({
            "id": template_id,
            "workspace_id": workspace_id
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await db.email_templates.update_one(
                {"id": template_id},
                {"$set": update_data}
            )
        
        updated = await db.email_templates.find_one({"id": template_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_email_template(template_id: str, workspace_id: str) -> bool:
        """Delete email template"""
        db = get_db()
        result = await db.email_templates.delete_one({
            "id": template_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def send_email(workspace_id: str, user_id: str, data: EmailSendRequest) -> dict:
        """
        Send email - MOCKED for now
        
        When ready to use real SendGrid:
        1. Set SENDGRID_API_KEY in backend/.env
        2. Uncomment the SendGrid integration code below
        3. Replace mock response with actual API call
        """
        db = get_db()
        
        # Get template if specified
        subject = data.subject
        body_html = data.bodyHtml
        
        if data.templateId:
            template = await db.email_templates.find_one({
                "id": data.templateId,
                "workspace_id": workspace_id
            })
            if template:
                subject = template.get("subject", subject)
                body_html = template.get("bodyHtml", body_html)
                
                # Simple variable substitution
                for key, value in data.variables.items():
                    body_html = body_html.replace(f"{{{{{key}}}}}", str(value))
                    subject = subject.replace(f"{{{{{key}}}}}", str(value))
        
        # === SENDGRID INTEGRATION (UNCOMMENT WHEN READY) ===
        # sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        # if sendgrid_api_key:
        #     import sendgrid
        #     from sendgrid.helpers.mail import Mail, Email, To, Content
        #     
        #     sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        #     from_email = Email(os.environ.get("SENDGRID_FROM_EMAIL", "noreply@enterprate.com"))
        #     
        #     for recipient in data.to:
        #         message = Mail(
        #             from_email=from_email,
        #             to_emails=To(recipient),
        #             subject=subject,
        #             html_content=Content("text/html", body_html)
        #         )
        #         response = sg.send(message)
        #         # Log the send...
        #     
        #     return {
        #         "success": True,
        #         "messageId": str(uuid.uuid4()),
        #         "message": f"Email sent to {len(data.to)} recipients",
        #         "mock": False
        #     }
        # === END SENDGRID INTEGRATION ===
        
        # MOCK RESPONSE
        email_log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Log the email attempt
        email_log = {
            "id": email_log_id,
            "workspace_id": workspace_id,
            "to": data.to,
            "subject": subject or "No subject",
            "bodyHtml": body_html,
            "templateId": data.templateId,
            "status": "sent",  # In mock mode, always "sent"
            "sentAt": now,
            "mock": True,
            "created_by": user_id
        }
        
        await db.email_logs.insert_one(email_log)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "email.sent",
            "data": {"email_log_id": email_log_id, "recipients": len(data.to), "mock": True},
            "occurredAt": now
        })
        
        return {
            "success": True,
            "messageId": email_log_id,
            "message": f"[MOCK] Email would be sent to {len(data.to)} recipient(s). Configure SENDGRID_API_KEY for real delivery.",
            "mock": True
        }
    
    @staticmethod
    async def get_email_logs(workspace_id: str, limit: int = 50) -> List[dict]:
        """Get email sending logs"""
        db = get_db()
        
        logs = await db.email_logs.find(
            {"workspace_id": workspace_id}
        ).sort("sentAt", -1).to_list(length=limit)
        
        return [{k: v for k, v in log.items() if k != '_id'} for log in logs]
    
    # === DOCUMENT MANAGEMENT ===
    
    @staticmethod
    async def create_document(workspace_id: str, user_id: str, data: DocumentCreate) -> dict:
        """Create document entry"""
        db = get_db()
        
        doc_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        document = {
            "id": doc_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "type": data.type,
            "description": data.description,
            "fileUrl": data.fileUrl,
            "content": data.content,
            "category": data.category,
            "tags": data.tags,
            "created_by": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.documents.insert_one(document)
        return {k: v for k, v in document.items() if k != '_id'}
    
    @staticmethod
    async def get_documents(workspace_id: str, category: Optional[str] = None) -> List[dict]:
        """Get documents for workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if category:
            query["category"] = category
        
        documents = await db.documents.find(query).sort("createdAt", -1).to_list(length=200)
        return [{k: v for k, v in doc.items() if k != '_id' and k != 'content'} for doc in documents]
    
    @staticmethod
    async def get_document(doc_id: str, workspace_id: str) -> dict:
        """Get a specific document"""
        db = get_db()
        
        document = await db.documents.find_one({
            "id": doc_id,
            "workspace_id": workspace_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {k: v for k, v in document.items() if k != '_id'}
    
    @staticmethod
    async def update_document(doc_id: str, workspace_id: str, data: DocumentUpdate) -> dict:
        """Update document"""
        db = get_db()
        
        document = await db.documents.find_one({
            "id": doc_id,
            "workspace_id": workspace_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        await db.documents.update_one(
            {"id": doc_id},
            {"$set": update_data}
        )
        
        updated = await db.documents.find_one({"id": doc_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_document(doc_id: str, workspace_id: str) -> bool:
        """Delete document"""
        db = get_db()
        result = await db.documents.delete_one({
            "id": doc_id,
            "workspace_id": workspace_id
        })
        return result.deleted_count > 0
    
    # === WORKFLOW TEMPLATES ===
    
    @staticmethod
    async def create_workflow(workspace_id: str, user_id: str, data: WorkflowTemplateCreate) -> dict:
        """Create workflow template"""
        db = get_db()
        
        workflow_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        workflow = {
            "id": workflow_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "description": data.description,
            "category": data.category,
            "steps": [step.model_dump() for step in data.steps],
            "trigger": data.trigger,
            "isActive": True,
            "created_by": user_id,
            "createdAt": now
        }
        
        await db.workflows.insert_one(workflow)
        return {k: v for k, v in workflow.items() if k != '_id'}
    
    @staticmethod
    async def get_workflows(workspace_id: str) -> List[dict]:
        """Get workflows for workspace"""
        db = get_db()
        
        workflows = await db.workflows.find(
            {"workspace_id": workspace_id}
        ).sort("createdAt", -1).to_list(length=100)
        
        return [{k: v for k, v in wf.items() if k != '_id'} for wf in workflows]
    
    @staticmethod
    async def get_default_workflows() -> List[dict]:
        """Get default workflow templates"""
        return [
            {
                "name": "New Client Onboarding",
                "description": "Automated workflow for new client setup",
                "category": "sales",
                "steps": [
                    {"id": "1", "title": "Send welcome email", "order": 1, "action": "email"},
                    {"id": "2", "title": "Create client folder", "order": 2, "action": "task"},
                    {"id": "3", "title": "Schedule kickoff call", "order": 3, "action": "task"},
                    {"id": "4", "title": "Send onboarding checklist", "order": 4, "action": "email"}
                ],
                "trigger": "manual"
            },
            {
                "name": "Invoice Follow-up",
                "description": "Automated payment reminder workflow",
                "category": "finance",
                "steps": [
                    {"id": "1", "title": "Send invoice", "order": 1, "action": "email"},
                    {"id": "2", "title": "Wait 7 days", "order": 2, "action": "wait"},
                    {"id": "3", "title": "Send reminder", "order": 3, "action": "email"},
                    {"id": "4", "title": "Create follow-up task", "order": 4, "action": "task"}
                ],
                "trigger": "event"
            },
            {
                "name": "Weekly Report",
                "description": "Generate and send weekly summary",
                "category": "operations",
                "steps": [
                    {"id": "1", "title": "Compile data", "order": 1, "action": "task"},
                    {"id": "2", "title": "Generate report", "order": 2, "action": "task"},
                    {"id": "3", "title": "Send to stakeholders", "order": 3, "action": "email"}
                ],
                "trigger": "scheduled"
            }
        ]
    
    # === AGENTIC EMAIL (HUMAN-IN-THE-LOOP) ===
    
    @staticmethod
    async def generate_email(workspace_id: str, user_id: str, data: dict) -> dict:
        """Generate email using AI for human review"""
        try:
            from emergentintegrations.llm.chat import LlmChat
            from emergentintegrations.llm.chat_types import UserMessage
            
            llm_key = os.environ.get("EMERGENT_LLM_KEY")
            if not llm_key:
                return OperationsService._get_fallback_email(data)
            
            llm = LlmChat(api_key=llm_key)
            
            recipient_name = data.get('recipientName', 'there')
            recipient_title = data.get('recipientTitle', '')
            company_name = data.get('companyName', 'Our Company')
            company_industry = data.get('companyIndustry', '')
            company_desc = data.get('companyDescription', '')
            
            prompt = f"""You are a professional business communications expert. Write a polished, grammatically perfect email.

RECIPIENT DETAILS:
- Name: {recipient_name}
- Title/Role: {recipient_title or 'Not specified'}

SENDER COMPANY:
- Company Name: {company_name}
- Industry: {company_industry or 'Not specified'}
- Description: {company_desc or 'Not specified'}

EMAIL REQUIREMENTS:
- Purpose: {data.get('purpose', 'General communication')}
- Tone: {data.get('tone', 'professional')}
- Include Call-to-Action: {data.get('includeCallToAction', True)}

CRITICAL RULES:
1. Address the recipient by their actual name (e.g., "Dear {recipient_name}," NOT "Dear [Recipient],")
2. Write in perfect British English with correct grammar and punctuation
3. Be specific and reference the context provided - do NOT use generic placeholder text
4. Keep the email concise yet comprehensive (3-5 paragraphs maximum)
5. End with a clear, specific call-to-action if requested
6. Use professional sign-off with the company name

Return ONLY a JSON object with this exact format:
{{
    "subject": "Clear, specific subject line",
    "body": "Complete email body with proper paragraphs"
}}"""
            
            response = await llm.send_message(
                model="gpt-4o",
                messages=[UserMessage(content=prompt)]
            )
            
            import json
            text = response if isinstance(response, str) else (response.text if hasattr(response, 'text') else str(response))
            print(f"Email generation raw response: {text[:200]}...")
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            result = json.loads(text.strip())
            
            return {
                "subject": result.get("subject", "Follow-up"),
                "body": result.get("body", ""),
                "generated": True,
                "to": data.get('recipientEmail', '')
            }
            
        except Exception as e:
            print(f"Email generation error: {e}")
            return OperationsService._get_fallback_email(data)
    
    @staticmethod
    def _get_fallback_email(data: dict) -> dict:
        """Fallback email when AI unavailable"""
        company = data.get('companyName', 'Our Company')
        recipient_name = data.get('recipientName', 'there')
        purpose = data.get('purpose', 'our recent conversation')
        
        return {
            "subject": f"Following Up - {company}",
            "body": f"""Dear {recipient_name},

I hope this message finds you well. I am reaching out regarding {purpose}.

At {company}, we are committed to delivering exceptional service and would be delighted to discuss how we can support your needs.

Would you be available for a brief call this week? Please let me know a time that works best for you.

Kind regards,
The {company} Team""",
            "generated": False,
            "to": data.get('recipientEmail', '')
        }
    
    @staticmethod
    async def get_pending_emails(workspace_id: str) -> List[dict]:
        """Get emails pending approval"""
        db = get_db()
        
        emails = await db.pending_emails.find(
            {"workspace_id": workspace_id, "status": "pending"}
        ).sort("createdAt", -1).to_list(length=50)
        
        return [{k: v for k, v in e.items() if k != '_id'} for e in emails]
    
    @staticmethod
    async def approve_email(email_id: str, workspace_id: str, user_id: str) -> dict:
        """Approve and send a pending email"""
        db = get_db()
        
        pending = await db.pending_emails.find_one({
            "id": email_id,
            "workspace_id": workspace_id
        })
        
        if not pending:
            raise HTTPException(status_code=404, detail="Pending email not found")
        
        # Actually send the email via SendGrid
        result = await OperationsService._send_via_sendgrid(
            to=pending.get("to", []),
            subject=pending.get("subject", ""),
            body_html=pending.get("bodyHtml", ""),
            workspace_id=workspace_id,
            user_id=user_id
        )
        
        # Mark as approved and sent
        await db.pending_emails.update_one(
            {"id": email_id},
            {"$set": {"status": "sent", "sentAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        return result
    
    @staticmethod
    async def reject_email(email_id: str, workspace_id: str) -> bool:
        """Reject a pending email"""
        db = get_db()
        
        result = await db.pending_emails.update_one(
            {"id": email_id, "workspace_id": workspace_id},
            {"$set": {"status": "rejected"}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def send_approved_email(workspace_id: str, user_id: str, data: dict) -> dict:
        """Send an approved email directly"""
        to_list = data.get("to", "").split(",") if isinstance(data.get("to"), str) else data.get("to", [])
        to_list = [t.strip() for t in to_list if t.strip()]
        
        if not to_list:
            raise HTTPException(status_code=400, detail="No recipients specified")
        
        return await OperationsService._send_via_sendgrid(
            to=to_list,
            subject=data.get("subject", ""),
            body_html=data.get("bodyHtml", ""),
            workspace_id=workspace_id,
            user_id=user_id
        )
    
    @staticmethod
    async def _send_via_sendgrid(to: List[str], subject: str, body_html: str, workspace_id: str, user_id: str) -> dict:
        """Actually send email via SendGrid"""
        db = get_db()
        sendgrid_key = os.environ.get("SENDGRID_API_KEY", "")
        from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@enterprate.com")
        
        email_log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if SendGrid is configured
        if sendgrid_key and not sendgrid_key.startswith("your-"):
            try:
                import sendgrid
                from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
                
                sg = sendgrid.SendGridAPIClient(api_key=sendgrid_key)
                
                for recipient in to:
                    message = Mail(
                        from_email=Email(from_email),
                        to_emails=To(recipient),
                        subject=subject,
                        html_content=HtmlContent(body_html)
                    )
                    sg.send(message)
                
                # Log success
                email_log = {
                    "id": email_log_id,
                    "workspace_id": workspace_id,
                    "to": to,
                    "subject": subject,
                    "bodyHtml": body_html,
                    "status": "sent",
                    "sentAt": now,
                    "mock": False,
                    "created_by": user_id
                }
                await db.email_logs.insert_one(email_log)
                
                return {
                    "success": True,
                    "messageId": email_log_id,
                    "message": f"Email sent to {len(to)} recipient(s)",
                    "mock": False
                }
                
            except Exception as e:
                print(f"SendGrid error: {e}")
                # Fall through to mock mode
        
        # Mock mode
        email_log = {
            "id": email_log_id,
            "workspace_id": workspace_id,
            "to": to,
            "subject": subject,
            "bodyHtml": body_html,
            "status": "sent",
            "sentAt": now,
            "mock": True,
            "created_by": user_id
        }
        await db.email_logs.insert_one(email_log)
        
        return {
            "success": True,
            "messageId": email_log_id,
            "message": f"[MOCK] Email logged for {len(to)} recipient(s)",
            "mock": True
        }
