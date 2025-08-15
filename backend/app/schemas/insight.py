from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IdeaInsightResponse(BaseModel):
    id: int
    idea_id: int
    market_insights: Optional[str] = None
    risk_assessment: Optional[str] = None
    implementation_roadmap: Optional[str] = None
    is_ai_generated: bool
    generation_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InsightSummary(BaseModel):
    idea_id: int
    idea_title: str
    market_insights: str
    risk_assessment: str
    implementation_roadmap: str
    is_ai_generated: bool
    generation_version: int
    generated_at: str
    last_updated: str
