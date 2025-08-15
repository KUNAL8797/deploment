from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class UserRole(str, enum.Enum):
    ADMIN = 'admin'
    CONTRIBUTOR = 'contributor'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CONTRIBUTOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with ideas
    ideas = relationship("Idea", back_populates="creator")
