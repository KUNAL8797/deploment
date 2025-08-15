from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import datetime

class DevelopmentStage(str, Enum):
    CONCEPT = "concept"
    RESEARCH = "research"
    PROTOTYPE = "prototype"
    TESTING = "testing"
    LAUNCH = "launch"

class IdeaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    development_stage: DevelopmentStage

class IdeaCreate(IdeaBase):
    """Schema for creating a new idea"""
    pass

class IdeaUpdate(BaseModel):
    """Schema for updating an existing idea"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    development_stage: Optional[DevelopmentStage] = None
    market_potential: Optional[float] = Field(None, ge=1.0, le=10.0)
    technical_complexity: Optional[float] = Field(None, ge=1.0, le=10.0)
    resource_requirements: Optional[float] = Field(None, ge=1.0, le=10.0)

class IdeaResponse(IdeaBase):
    """Schema for idea responses"""
    id: int
    ai_validated: bool
    ai_refined_pitch: Optional[str] = None
    market_potential: Optional[float] = None
    technical_complexity: Optional[float] = None
    resource_requirements: Optional[float] = None
    feasibility_score: float
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IdeaListResponse(BaseModel):
    """Schema for paginated idea list responses"""
    items: List[IdeaResponse]
    total: int
    skip: int
    limit: int
    has_next: bool
