"""Genesis AI routes for Business/Product Idea Validation"""
from fastapi import APIRouter, Depends, Header
from app.services.genesis_service import GenesisService
from app.schemas.genesis import (
    ValidationIdeaRequest,
    ValidationIdeaResponse,
    IdeaScoreRequest, 
    IdeaScoreResponse
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/genesis", tags=["genesis"])

@router.post("/validate", response_model=ValidationIdeaResponse)
async def validate_idea(
    data: ValidationIdeaRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Validate a business or product idea with full scoring framework.
    
    Returns comprehensive validation report including:
    - Overall score (0-100)
    - Score breakdown by category
    - Verdict (PASS/PIVOT/KILL)
    - Strengths, weaknesses, risks
    - Actionable recommendations
    - Next validation experiments
    """
    await verify_workspace_access(workspace_id, user)
    return await GenesisService.validate_idea(workspace_id, user["id"], data)

@router.post("/idea-score", response_model=IdeaScoreResponse)
async def score_idea(
    data: IdeaScoreRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Legacy simple idea scoring endpoint"""
    await verify_workspace_access(workspace_id, user)
    return await GenesisService.score_idea(workspace_id, user["id"], data)
