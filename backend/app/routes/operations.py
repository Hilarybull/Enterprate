"""Operations routes - Tasks, Email, Documents, Workflows"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.services.operations_service import OperationsService
from app.schemas.operations import (
    TaskCreate, TaskUpdate, TaskResponse,
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse,
    EmailSendRequest, EmailSendResponse, EmailLogResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse,
    WorkflowTemplateCreate, WorkflowTemplateResponse
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/operations", tags=["operations"])


# === TASK ENDPOINTS ===

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new task"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.create_task(workspace_id, user["id"], data)


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get tasks for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_tasks(workspace_id, status, project_id)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a task"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.update_task(task_id, workspace_id, data)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a task"""
    await verify_workspace_access(workspace_id, user)
    deleted = await OperationsService.delete_task(task_id, workspace_id)
    return {"deleted": deleted}


@router.get("/tasks/stats")
async def get_task_stats(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get task statistics"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_task_stats(workspace_id)


# === EMAIL TEMPLATE ENDPOINTS ===

@router.post("/email-templates", response_model=EmailTemplateResponse)
async def create_email_template(
    data: EmailTemplateCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create email template"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.create_email_template(workspace_id, user["id"], data)


@router.get("/email-templates", response_model=List[EmailTemplateResponse])
async def get_email_templates(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all email templates"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_email_templates(workspace_id)


@router.patch("/email-templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: str,
    data: EmailTemplateUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update email template"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.update_email_template(template_id, workspace_id, data)


@router.delete("/email-templates/{template_id}")
async def delete_email_template(
    template_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete email template"""
    await verify_workspace_access(workspace_id, user)
    deleted = await OperationsService.delete_email_template(template_id, workspace_id)
    return {"deleted": deleted}


# === EMAIL SENDING (MOCKED) ===

@router.post("/send-email", response_model=EmailSendResponse)
async def send_email(
    data: EmailSendRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Send email - Currently MOCKED.
    
    To enable real sending:
    1. Add SENDGRID_API_KEY to backend/.env
    2. Add SENDGRID_FROM_EMAIL to backend/.env
    """
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.send_email(workspace_id, user["id"], data)


@router.get("/email-logs", response_model=List[EmailLogResponse])
async def get_email_logs(
    limit: int = Query(50, le=200),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get email sending logs"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_email_logs(workspace_id, limit)


# === DOCUMENT ENDPOINTS ===

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    data: DocumentCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create document entry"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.create_document(workspace_id, user["id"], data)


@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    category: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get documents for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_documents(workspace_id, category)


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a specific document"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_document(doc_id, workspace_id)


@router.patch("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: str,
    data: DocumentUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update document"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.update_document(doc_id, workspace_id, data)


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete document"""
    await verify_workspace_access(workspace_id, user)
    deleted = await OperationsService.delete_document(doc_id, workspace_id)
    return {"deleted": deleted}


# === WORKFLOW ENDPOINTS ===

@router.post("/workflows", response_model=WorkflowTemplateResponse)
async def create_workflow(
    data: WorkflowTemplateCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create workflow template"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.create_workflow(workspace_id, user["id"], data)


@router.get("/workflows", response_model=List[WorkflowTemplateResponse])
async def get_workflows(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get workflows for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_workflows(workspace_id)


@router.get("/workflows/defaults")
async def get_default_workflows(
    user: dict = Depends(get_current_user)
):
    """Get default workflow templates"""
    return await OperationsService.get_default_workflows()


# === AGENTIC EMAIL (HUMAN-IN-THE-LOOP) ===

@router.post("/generate-email")
async def generate_email(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate email draft using AI for human review"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.generate_email(workspace_id, user["id"], data)


@router.get("/pending-emails")
async def get_pending_emails(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get emails pending approval"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.get_pending_emails(workspace_id)


@router.post("/approve-email/{email_id}")
async def approve_email(
    email_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Approve and send a pending email"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.approve_email(email_id, workspace_id, user["id"])


@router.post("/reject-email/{email_id}")
async def reject_email(
    email_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Reject a pending email"""
    await verify_workspace_access(workspace_id, user)
    rejected = await OperationsService.reject_email(email_id, workspace_id)
    return {"rejected": rejected}


@router.post("/send-approved-email")
async def send_approved_email(
    data: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Send an approved email directly"""
    await verify_workspace_access(workspace_id, user)
    return await OperationsService.send_approved_email(workspace_id, user["id"], data)
