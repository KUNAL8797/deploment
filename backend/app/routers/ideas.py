from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text  # ← ADD THIS LINE
from typing import Optional
import logging

from ..database import get_db
from ..models.idea import Idea, DevelopmentStage
from ..schemas.idea import IdeaCreate, IdeaUpdate, IdeaResponse, IdeaListResponse
from ..auth.auth import get_current_user
from ..models.user import User
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(
    idea: IdeaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new innovation idea"""
    try:
        # Create new idea
        db_idea = Idea(
            title=idea.title,
            description=idea.description,
            development_stage=idea.development_stage,
            created_by=current_user.id,
            # Set default scores (AI will enhance these later)
            market_potential=5.0,
            technical_complexity=5.0,
            resource_requirements=5.0
        )
        
        db.add(db_idea)
        db.commit()
        db.refresh(db_idea)
        
        logger.info(f"Created new idea '{db_idea.title}' by user {current_user.username}")
        return db_idea
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating idea: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create idea"
        )

@router.get("/", response_model=IdeaListResponse)
async def list_ideas(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    stage: Optional[DevelopmentStage] = Query(None, description="Filter by development stage"),
    ai_validated: Optional[bool] = Query(None, description="Filter by AI validation status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: Session = Depends(get_db)
):
    """List ideas with filtering, pagination, and search"""
    try:
        query = db.query(Idea)
        
        # Apply filters
        if stage:
            query = query.filter(Idea.development_stage == stage)
        if ai_validated is not None:
            query = query.filter(Idea.ai_validated == ai_validated)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Idea.title.ilike(search_filter)) |
                (Idea.description.ilike(search_filter))
            )
        
        # Count total items
        total = query.count()
        
        # Apply sorting and pagination
        items = query.order_by(Idea.created_at.desc()).offset(skip).limit(limit).all()
        
        return IdeaListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total
        )
        
    except Exception as e:
        logger.error(f"Error listing ideas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ideas"
        )

@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(idea_id: int, db: Session = Depends(get_db)):
    """Get a specific idea by ID"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    return idea

@router.put("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: int,
    idea_update: IdeaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing idea"""
    db_idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not db_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Check if user owns this idea
    if db_idea.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this idea"
        )
    
    # Update fields
    update_data = idea_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_idea, field, value)
    
    db.commit()
    db.refresh(db_idea)
    return db_idea

@router.delete("/{idea_id}")
async def delete_idea(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an idea"""
    db_idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not db_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Check if user owns this idea
    if db_idea.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this idea"
        )
    
    db.delete(db_idea)
    db.commit()
    return {"message": "Idea deleted successfully"}

# Debug endpoint


# ... (keep all your existing endpoints: create_idea, list_ideas, get_idea, update_idea, delete_idea)

# REPLACE THE DEBUG ENDPOINT WITH THIS CORRECTED VERSION:
@router.get("/debug/database-check")
async def check_database(db: Session = Depends(get_db)):
    """Debug endpoint to check database connection and tables"""
    try:
        # Test basic database connection using text()
        result = db.execute(text("SELECT 1 as test")).fetchone()
        logger.info(f"Database connection test: {result}")
        
        # Count ideas and users using ORM (preferred method)
        ideas_count = db.query(Idea).count()
        users_count = db.query(User).count()
        
        # Get sample data using ORM
        sample_ideas = db.query(Idea).limit(3).all()
        sample_users = db.query(User).limit(3).all()
        
        return {
            "database_connection": "OK",
            "connection_test_result": result[0] if result else None,
            "ideas_count": ideas_count,
            "users_count": users_count,
            "sample_ideas": [
                {
                    "id": idea.id, 
                    "title": idea.title, 
                    "created_by": idea.created_by,
                    "development_stage": idea.development_stage.value,
                    "ai_validated": idea.ai_validated
                } 
                for idea in sample_ideas
            ],
            "sample_users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value
                }
                for user in sample_users
            ],
            "tables_created": "Successfully using SQLAlchemy ORM"
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Database check failed: {str(e)}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "Database connection failed"
        }
