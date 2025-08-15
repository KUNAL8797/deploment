from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
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
            # Set default scores for now (AI will enhance these later)
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
    sort_by: Optional[str] = Query("created_at", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """List ideas with filtering, pagination, and search"""
    try:
        print(f"Starting list_ideas with skip={skip}, limit={limit}")  # Debug log
        
        query = db.query(Idea)
        print(f"Base query created successfully")  # Debug log
        
        # Apply filters
        if stage:
            query = query.filter(Idea.development_stage == stage)
            print(f"Applied stage filter: {stage}")
            
        if ai_validated is not None:
            query = query.filter(Idea.ai_validated == ai_validated)
            print(f"Applied ai_validated filter: {ai_validated}")
            
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Idea.title.ilike(search_filter)) |
                (Idea.description.ilike(search_filter))
            )
            print(f"Applied search filter: {search}")
        
        # Count total items before pagination
        print("Counting total items...")
        total = query.count()
        print(f"Total items found: {total}")
        
        # Apply sorting (simplified for debugging)
        query = query.order_by(Idea.created_at.desc())
        
        # Apply pagination
        print(f"Applying pagination: offset={skip}, limit={limit}")
        items = query.offset(skip).limit(limit).all()
        print(f"Retrieved {len(items)} items")
        
        return IdeaListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total
        )
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"ERROR in list_ideas: {str(e)}")
        print(f"Full traceback:\n{tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ideas: {str(e)}"
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
