"""Genesis AI schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List, Any

class IdeaScoreRequest(BaseModel):
    idea: str
    targetCustomer: Optional[str] = None

class IdeaScoreResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    score: int
    analysis: Dict[str, int]
    insights: List[str]
    nextSteps: List[str]
