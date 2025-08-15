from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class DevelopmentStage(str, enum.Enum):
    CONCEPT = "concept"
    RESEARCH = "research"
    PROTOTYPE = "prototype"
    TESTING = "testing"
    LAUNCH = "launch"

class Idea(Base):
    __tablename__ = "ideas"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields for assignment
    title = Column(String(200), nullable=False)                    # Text field
    description = Column(Text, nullable=False)                     # Text field
    development_stage = Column(Enum(DevelopmentStage), nullable=False)  # Enum field
    ai_validated = Column(Boolean, default=False)                  # Boolean field
    
    # AI-generated content (will be populated later)
    ai_refined_pitch = Column(Text, nullable=True)
    
    # Fields for calculated field (feasibility_score)
    market_potential = Column(DECIMAL(3,1), nullable=True, default=5.0)
    technical_complexity = Column(DECIMAL(3,1), nullable=True, default=5.0) 
    resource_requirements = Column(DECIMAL(3,1), nullable=True, default=5.0)
    
    # Calculated field - this will be computed automatically
    # feasibility_score = (market_potential + (11 - technical_complexity) + (11 - resource_requirements)) / 3
    
    # User relationship
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="ideas")
    
    # Property for calculated field
    @property
    def feasibility_score(self) -> float:
        """Calculate feasibility score from market potential, technical complexity, and resource requirements"""
        if all([self.market_potential, self.technical_complexity, self.resource_requirements]):
            return round(
                (float(self.market_potential) + 
                 (11 - float(self.technical_complexity)) + 
                 (11 - float(self.resource_requirements))) / 3, 
                2
            )
        return 0.0
