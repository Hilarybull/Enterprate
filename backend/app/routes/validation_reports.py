"""Comprehensive Validation Reports API routes"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.validation_report_service import ValidationReportService
from app.schemas.validation_report import (
    ValidationReportCreate,
    ValidationReportResponse,
    ValidationReportListItem,
    ReportStatusUpdate,
    EngagementStats,
    ReportStatus
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/validation-reports", tags=["validation-reports"])


@router.post("", response_model=dict)
async def create_validation_report(
    data: ValidationReportCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Create a comprehensive IdeaBrowser-style validation report.
    
    This endpoint generates an AI-powered analysis including:
    - Opportunity, Problem, Feasibility, and Timing scores
    - Business fit analysis
    - Value ladder recommendations
    - Framework analysis
    - Community signals and keyword data
    """
    await verify_workspace_access(workspace_id, user)
    return await ValidationReportService.create_comprehensive_report(
        workspace_id, user["id"], data
    )


@router.get("", response_model=List[ValidationReportListItem])
async def list_validation_reports(
    limit: int = 50,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    List all validation reports for the current user.
    
    Returns a summary list with:
    - Report ID and idea name
    - Status (pending/accepted/rejected)
    - Overall score and verdict
    - Creation date
    """
    await verify_workspace_access(workspace_id, user)
    return await ValidationReportService.get_user_reports(
        workspace_id, user["id"], limit
    )


@router.get("/engagement", response_model=EngagementStats)
async def get_engagement_stats(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Get user's validation engagement statistics.
    
    Returns:
    - Total number of validations
    - Count by status (accepted, rejected, pending)
    """
    await verify_workspace_access(workspace_id, user)
    return await ValidationReportService.get_engagement_stats(
        workspace_id, user["id"]
    )


@router.get("/{report_id}", response_model=dict)
async def get_validation_report(
    report_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Get a specific validation report by ID.
    
    Returns the full report including:
    - Original input data
    - Complete analysis report
    - Current status
    """
    await verify_workspace_access(workspace_id, user)
    report = await ValidationReportService.get_report_by_id(report_id, workspace_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.put("/{report_id}/status")
async def update_report_status(
    report_id: str,
    status_update: ReportStatusUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Update the status of a validation report (accept/reject).
    
    Status options:
    - pending: Initial state
    - accepted: User accepts the idea
    - rejected: User rejects the idea
    """
    await verify_workspace_access(workspace_id, user)
    
    result = await ValidationReportService.update_report_status(
        report_id, workspace_id, status_update.status
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": f"Report status updated to {status_update.status.value}", "report": result}


@router.post("/{report_id}/modify", response_model=dict)
async def modify_and_regenerate(
    report_id: str,
    new_data: ValidationReportCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Modify the input data and regenerate the validation report.
    
    This allows users to:
    - Edit their original idea inputs
    - Get a fresh AI analysis with updated information
    - Status is reset to 'pending'
    """
    await verify_workspace_access(workspace_id, user)
    
    result = await ValidationReportService.modify_and_regenerate(
        report_id, workspace_id, user["id"], new_data
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return result


@router.delete("/{report_id}")
async def delete_validation_report(
    report_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a validation report"""
    await verify_workspace_access(workspace_id, user)
    
    success = await ValidationReportService.delete_report(report_id, workspace_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": "Report deleted successfully"}
