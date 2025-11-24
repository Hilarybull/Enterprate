"""Genesis AI routes"""
from fastapi import APIRouter, Depends
from app.schemas.genesis import IdeaScoreRequest, BusinessBlueprintRequest
from app.services.genesis_service import GenesisService
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access

router = APIRouter(prefix="/genesis", tags=["genesis-ai"])

@router.post("/idea-score")
async def score_idea(
    request: IdeaScoreRequest,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Score a business idea using AI"""
    await verify_workspace_access(workspace_id, user)
    return await GenesisService.score_idea(request, workspace_id, user['id'])

@router.post("/business-blueprint")
async def create_blueprint(
    request: BusinessBlueprintRequest,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Create a business blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await GenesisService.create_blueprint(request)
