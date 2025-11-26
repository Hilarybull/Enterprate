"""Genesis AI routes"""
from fastapi import APIRouter, Depends, Header
from app.services.genesis_service import GenesisService
from app.schemas.genesis import IdeaScoreRequest, IdeaScoreResponse
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/genesis", tags=["genesis"])

@router.post("/idea-score", response_model=IdeaScoreResponse)
async def score_idea(
    data: IdeaScoreRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Score a business idea"""
    await verify_workspace_access(workspace_id, user)
    return await GenesisService.score_idea(workspace_id, user["id"], data)
