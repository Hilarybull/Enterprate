"""Genesis AI-related schemas"""
from pydantic import BaseModel
from typing import Optional

class IdeaScoreRequest(BaseModel):
    idea: str
    targetCustomer: Optional[str] = None

class BusinessBlueprintRequest(BaseModel):
    businessName: str
    industry: str
    targetMarket: str
