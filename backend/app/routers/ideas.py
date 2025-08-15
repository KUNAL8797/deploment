from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text  # ← ADD THIS LINE
from typing import Optional
import logging
from datetime import datetime
import logging
# ... other imports
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
    """Create a new innovation idea with AI enhancement"""
    try:
        # Create basic idea first
        db_idea = Idea(
            title=idea.title,
            description=idea.description,
            development_stage=idea.development_stage,
            created_by=current_user.id,
            market_potential=5.0,
            technical_complexity=5.0,
            resource_requirements=5.0,
            ai_validated=False  # ← Start as False
        )
        
        db.add(db_idea)
        db.commit()
        db.refresh(db_idea)
        
        logger.info(f"Created basic idea {db_idea.id} for user {current_user.username}")
        
        # AI Enhancement
        try:
            from ..services.ai_service import ai_service
            
            logger.info(f"Starting AI enhancement for idea {db_idea.id}")
            
            # Step 1: AI refinement
            refined_pitch = await ai_service.refine_idea(
                db_idea.title, 
                db_idea.description, 
                db_idea.development_stage.value
            )
            db_idea.ai_refined_pitch = refined_pitch
            logger.info(f"AI refinement completed for idea {db_idea.id}")
            
            # Step 2: Feasibility analysis
            idea_data = {
                "title": db_idea.title,
                "description": db_idea.description,
                "ai_refined_pitch": refined_pitch,
                "development_stage": db_idea.development_stage.value
            }
            
            market, complexity, resources = await ai_service.generate_feasibility_analysis(idea_data)
            db_idea.market_potential = market
            db_idea.technical_complexity = complexity
            db_idea.resource_requirements = resources
            
            # ← CRITICAL: Set AI validated flag to True
            logger.info(f"Setting ai_validated=True for idea {db_idea.id}")
            db_idea.ai_validated = True
            
            # ← CRITICAL: Commit the changes
            db.commit()
            db.refresh(db_idea)
            
            logger.info(f"✅ AI enhancement completed and saved for idea {db_idea.id}")
            
        except Exception as ai_error:
            logger.error(f"❌ AI enhancement failed for idea {db_idea.id}: {ai_error}")
            # Idea remains with ai_validated=False
            
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ADD THIS LINE
):
    """List ideas filtered by current authenticated user only"""
    try:
        # ← ADD THIS CRITICAL FILTER
        query = db.query(Idea).filter(Idea.created_by == current_user.id)
        
        # Apply additional filters
        if stage:
            query = query.filter(Idea.development_stage == stage)
        if ai_validated is not None:
            query = query.filter(Idea.ai_validated == ai_validated)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Idea.title.ilike(search_filter)) |
                (Idea.description.ilike(search_filter)) |
                (Idea.ai_refined_pitch.ilike(search_filter))
            )
        
        # Count total items for this user only
        total = query.count()
        
        # Apply sorting
        if sort_by == "feasibility_score":
            if sort_order == "desc":
                query = query.order_by(
                    ((Idea.market_potential + (11 - Idea.technical_complexity) + (11 - Idea.resource_requirements)) / 3).desc()
                )
            else:
                query = query.order_by(
                    ((Idea.market_potential + (11 - Idea.technical_complexity) + (11 - Idea.resource_requirements)) / 3).asc()
                )
        elif sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(Idea.created_at.desc())
            else:
                query = query.order_by(Idea.created_at.asc())
        elif sort_by == "title":
            if sort_order == "desc":
                query = query.order_by(Idea.title.desc())
            else:
                query = query.order_by(Idea.title.asc())
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.username} retrieved {len(items)} of {total} personal ideas")
        
        return IdeaListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total
        )
        
    except Exception as e:
        logger.error(f"Error listing ideas for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ideas"
        )


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ADD THIS
):
    """Get a specific idea by ID - only if owned by current user"""
    idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.created_by == current_user.id  # ← ADD THIS SECURITY CHECK
    ).first()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found or not accessible"
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
async def check_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ADD THIS
):
    """Debug endpoint - user-specific data only"""
    try:
        # Test basic database connection
        result = db.execute(text("SELECT 1 as test")).fetchone()
        
        # Count user's specific data
        user_ideas_count = db.query(Idea).filter(Idea.created_by == current_user.id).count()
        total_users_count = db.query(User).count()
        
        # Get user's sample ideas only
        user_sample_ideas = db.query(Idea).filter(Idea.created_by == current_user.id).limit(3).all()
        
        return {
            "database_connection": "OK",
            "connection_test_result": result[0] if result else None,
            "current_user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            },
            "user_ideas_count": user_ideas_count,
            "total_users_in_system": total_users_count,
            "user_sample_ideas": [
                {
                    "id": idea.id,
                    "title": idea.title,
                    "development_stage": idea.development_stage.value,
                    "ai_validated": idea.ai_validated,
                    "feasibility_score": idea.feasibility_score
                }
                for idea in user_sample_ideas
            ],
            "privacy_check": "✅ Only showing current user's data"
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Database check failed for user {current_user.id}: {str(e)}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "Database connection failed"
        }
@router.post("/{idea_id}/enhance", response_model=IdeaResponse)
async def enhance_idea_with_ai(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger AI enhancement and validation"""
    # Find user's idea
    db_idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.created_by == current_user.id
    ).first()
    
    if not db_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    try:
        from ..services.ai_service import ai_service
        
        logger.info(f"Manual AI enhancement started for idea {idea_id}")
        
        # AI refinement
        refined_pitch = await ai_service.refine_idea(
            db_idea.title,
            db_idea.description,
            db_idea.development_stage.value
        )
        db_idea.ai_refined_pitch = refined_pitch
        
        # Feasibility analysis
        idea_data = {
            "title": db_idea.title,
            "description": db_idea.description,
            "ai_refined_pitch": refined_pitch,
            "development_stage": db_idea.development_stage.value
        }
        
        market, complexity, resources = await ai_service.generate_feasibility_analysis(idea_data)
        db_idea.market_potential = market
        db_idea.technical_complexity = complexity
        db_idea.resource_requirements = resources
        
        # ← CRITICAL: Set validation flag
        logger.info(f"Setting ai_validated=True for idea {idea_id}")
        db_idea.ai_validated = True
        
        # ← CRITICAL: Save changes
        db.commit()
        db.refresh(db_idea)
        
        logger.info(f"✅ Manual AI enhancement completed for idea {idea_id}")
        
        return db_idea
        
    except Exception as e:
        logger.error(f"❌ Manual AI enhancement failed for idea {idea_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI enhancement failed: {str(e)}"
        )
from datetime import datetime
from ..models.insight import IdeaInsight
from ..schemas.insight import InsightSummary

@router.get("/{idea_id}/insights", response_model=InsightSummary)
async def get_idea_insights(
    idea_id: int,
    force_regenerate: bool = Query(False, description="Force regenerate insights even if they exist"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive AI insights for an idea - saved to database"""
    # Find the user's idea
    db_idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.created_by == current_user.id
    ).first()
    
    if not db_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Check if insights already exist and not forcing regeneration
    existing_insights = db.query(IdeaInsight).filter(
        IdeaInsight.idea_id == idea_id
    ).first()
    
    if existing_insights and not force_regenerate:
        logger.info(f"Returning existing insights for idea {idea_id}")
        return InsightSummary(
            idea_id=idea_id,
            idea_title=db_idea.title,
            market_insights=existing_insights.market_insights or "Market insights not available",
            risk_assessment=existing_insights.risk_assessment or "Risk assessment not available",
            implementation_roadmap=existing_insights.implementation_roadmap or "Implementation roadmap not available",
            is_ai_generated=existing_insights.is_ai_generated,
            generation_version=existing_insights.generation_version,
            generated_at=existing_insights.created_at.isoformat(),
            last_updated=existing_insights.updated_at.isoformat()
        )
    
    try:
        from ..services.ai_service import ai_service
        
        logger.info(f"Starting comprehensive insights generation for idea {idea_id}")
        
        # Prepare data for AI calls
        idea_data = {
            "title": db_idea.title,
            "description": db_idea.description,
            "ai_refined_pitch": db_idea.ai_refined_pitch,
            "development_stage": db_idea.development_stage.value,
            "market_potential": float(db_idea.market_potential or 5.0),
            "technical_complexity": float(db_idea.technical_complexity or 5.0),
            "resource_requirements": float(db_idea.resource_requirements or 5.0)
        }
        
        # Initialize tracking variables
        is_ai_generated = True
        market_insights = ""
        risk_assessment = ""
        implementation_roadmap = ""
        
        # Generate market insights with error handling
        try:
            logger.info(f"Generating market insights for idea {idea_id}")
            market_insights = await ai_service.generate_market_insights(
                db_idea.title, 
                db_idea.description,
                db_idea.ai_refined_pitch or db_idea.description
            )
            logger.info(f"Market insights generated successfully for idea {idea_id}")
        except Exception as e:
            logger.error(f"Market insights failed for idea {idea_id}: {e}")
            market_insights = f"**Market Analysis for {db_idea.title}**\n\nMarket analysis temporarily unavailable. Please try again later."
            is_ai_generated = False
        
        # Generate risk assessment with error handling
        try:
            logger.info(f"Generating risk assessment for idea {idea_id}")
            risk_assessment = await ai_service.generate_risk_assessment(idea_data)
            logger.info(f"Risk assessment generated successfully for idea {idea_id}")
        except Exception as e:
            logger.error(f"Risk assessment failed for idea {idea_id}: {e}")
            risk_assessment = f"**Risk Assessment for {db_idea.title}**\n\nRisk analysis temporarily unavailable. Please try again later."
            is_ai_generated = False
        
        # Generate implementation roadmap with error handling
        try:
            logger.info(f"Generating implementation roadmap for idea {idea_id}")
            implementation_roadmap = await ai_service.generate_implementation_roadmap(idea_data)
            logger.info(f"Implementation roadmap generated successfully for idea {idea_id}")
        except Exception as e:
            logger.error(f"Implementation roadmap failed for idea {idea_id}: {e}")
            implementation_roadmap = f"**Implementation Roadmap for {db_idea.title}**\n\nImplementation planning temporarily unavailable. Please try again later."
            is_ai_generated = False
        
        # Save or update insights in database
        if existing_insights:
            # Update existing insights
            existing_insights.market_insights = market_insights
            existing_insights.risk_assessment = risk_assessment
            existing_insights.implementation_roadmap = implementation_roadmap
            existing_insights.is_ai_generated = is_ai_generated
            existing_insights.generation_version += 1
            existing_insights.updated_at = datetime.now()
            
            logger.info(f"Updated existing insights for idea {idea_id} (version {existing_insights.generation_version})")
            
        else:
            # Create new insights record
            new_insights = IdeaInsight(
                idea_id=idea_id,
                market_insights=market_insights,
                risk_assessment=risk_assessment,
                implementation_roadmap=implementation_roadmap,
                is_ai_generated=is_ai_generated,
                generation_version=1
            )
            db.add(new_insights)
            existing_insights = new_insights
            
            logger.info(f"Created new insights record for idea {idea_id}")
        
        # Commit to database
        db.commit()
        db.refresh(existing_insights)
        
        logger.info(f"✅ All insights generated and saved to database for idea {idea_id}")
        
        return InsightSummary(
            idea_id=idea_id,
            idea_title=db_idea.title,
            market_insights=existing_insights.market_insights,
            risk_assessment=existing_insights.risk_assessment,
            implementation_roadmap=existing_insights.implementation_roadmap,
            is_ai_generated=existing_insights.is_ai_generated,
            generation_version=existing_insights.generation_version,
            generated_at=existing_insights.created_at.isoformat(),
            last_updated=existing_insights.updated_at.isoformat()
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Critical error generating insights for idea {idea_id}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI insights: {str(e)}"
        )

@router.delete("/{idea_id}/insights")
async def delete_idea_insights(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete stored insights for an idea"""
    # Verify idea ownership
    db_idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.created_by == current_user.id
    ).first()
    
    if not db_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Delete insights
    insights = db.query(IdeaInsight).filter(IdeaInsight.idea_id == idea_id).first()
    if insights:
        db.delete(insights)
        db.commit()
        logger.info(f"Deleted insights for idea {idea_id}")
        
        return {"message": "Insights deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No insights found for this idea"
        )

@router.get("/{idea_id}/insights/history")
async def get_insights_history(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights generation history for an idea"""
    # Verify idea ownership
    db_idea = db.query(Idea).filter(
        Idea.id == idea_id,
        Idea.created_by == current_user.id
    ).first()
    
    if not db_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    insights = db.query(IdeaInsight).filter(IdeaInsight.idea_id == idea_id).first()
    
    if not insights:
        return {
            "idea_id": idea_id,
            "has_insights": False,
            "insights_count": 0
        }
    
    return {
        "idea_id": idea_id,
        "has_insights": True,
        "insights_count": 1,
        "current_version": insights.generation_version,
        "first_generated": insights.created_at.isoformat(),
        "last_updated": insights.updated_at.isoformat(),
        "is_ai_generated": insights.is_ai_generated
    }


