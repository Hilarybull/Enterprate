"""Business Documents Routes"""
from fastapi import APIRouter, Depends, Response
from typing import Optional
from app.core.security import get_current_user, get_workspace_id
from app.services.document_service import (
    DocumentService,
    DocumentGenerateRequest,
    DocumentSaveRequest,
    DocumentExportRequest
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def get_documents(
    doc_type: Optional[str] = None,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all documents for workspace"""
    return await DocumentService.get_documents(workspace_id, doc_type)


@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a single document"""
    return await DocumentService.get_document(doc_id, workspace_id)


@router.post("/generate")
async def generate_document(
    data: DocumentGenerateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate a document using the wizard"""
    return await DocumentService.generate_document(workspace_id, user["id"], data)


@router.post("/save")
async def save_document(
    data: DocumentSaveRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Save a generated document"""
    return await DocumentService.save_document(workspace_id, user["id"], data)


@router.post("/export")
async def export_document(
    data: DocumentExportRequest,
    user: dict = Depends(get_current_user)
):
    """Export document to PDF or DOCX"""
    content = await DocumentService.export_document(data)
    
    media_type = "application/pdf" if data.format == "pdf" else "text/plain"
    filename = f"{data.title}.{data.format}"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
