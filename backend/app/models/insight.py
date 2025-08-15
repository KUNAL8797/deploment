from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class IdeaInsight(Base):
    __tablename__ = "idea_insights"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    
    # AI-generated insights content
    market_insights = Column(Text, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    implementation_roadmap = Column(Text, nullable=True)
    
    # Metadata
    is_ai_generated = Column(Boolean, default=True)  # Track if AI-generated or fallback
    generation_version = Column(Integer, default=1)  # Track regenerations
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    idea = relationship("Idea", back_populates="insights")
