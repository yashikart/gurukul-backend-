
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.summary import (
    SubjectExplorerRequest, SubjectExplorerResponse, SaveSummaryRequest
)
from app.models.all_models import Summary as DBSummary, User, SubjectData
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.services.ems_sync import ems_sync
from sqlalchemy.orm import Session
from app.services.llm import call_groq_api, call_ollama_api
from app.services.youtube import get_youtube_recommendations
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/explore", response_model=SubjectExplorerResponse)
async def subject_explorer(
    request: SubjectExplorerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Explore a subject/topic to get comprehensive notes and resources.
    Saves to DB and syncs to EMS.
    """
    print(f"\n[API] Received /subject-explorer request: {request.subject} - {request.topic}")
    
    # 1. Generate Notes using LLM
    try:
        if request.provider == "groq":
            notes = await call_groq_api(request.subject, request.topic)
        elif request.provider == "ollama":
            notes = await call_ollama_api(request.subject, request.topic)
        else:
            # Default to Groq
            notes = await call_groq_api(request.subject, request.topic)
    except Exception as e:
        print(f"[API] LLM Error: {str(e)}")
        # Fallback notes
        notes = f"# Error Generating Notes\n\nCould not generate notes for {request.topic}. Please try again."

    # 2. Get YouTube Recommendations
    youtube_videos = []
    try:
        youtube_videos = await get_youtube_recommendations(request.subject, request.topic)
    except Exception as e:
        print(f"[API] YouTube Error: {str(e)}")
    
    # 3. Save to database
    subject_data = SubjectData(
        user_id=current_user.id,
        subject=request.subject,
        topic=request.topic,
        notes=notes,
        provider=request.provider,
        youtube_recommendations=youtube_videos
    )
    db.add(subject_data)
    db.commit()
    db.refresh(subject_data)
    
    # 4. Sync to EMS asynchronously (don't block response)
    try:
        # Get school_id from user if available
        school_id = getattr(current_user, 'school_id', None)
        
        ems_sync_result = await ems_sync.sync_subject_data(
            gurukul_id=subject_data.id,
            student_email=current_user.email,
            school_id=school_id,
            subject=request.subject,
            topic=request.topic,
            notes=notes,
            provider=request.provider,
            youtube_recommendations=youtube_videos
        )
        
        if ems_sync_result:
            subject_data.ems_sync_id = ems_sync_result.get("id")
            subject_data.synced_to_ems = True
            db.commit()
            logger.info(f"Synced subject data {subject_data.id} to EMS")
    except Exception as e:
        logger.error(f"Failed to sync subject data {subject_data.id} to EMS: {str(e)}")
        # Don't fail the request if sync fails
        
    return SubjectExplorerResponse(
        subject=request.subject,
        topic=request.topic,
        notes=notes,
        provider=request.provider,
        youtube_recommendations=youtube_videos,
        success=True
    )

@router.post("/summaries/save")
async def save_learning_summary(
    summary_in: SaveSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a summary for flashcard generation or review - syncs to EMS"""
    # Create DB entry
    new_summary = DBSummary(
        user_id=current_user.id,
        title=summary_in.title,
        content=summary_in.content,
        source=summary_in.source or "manual",
        source_type=summary_in.source_type or "text"
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    
    # Sync to EMS asynchronously (don't block response)
    try:
        # Get school_id from user if available
        school_id = getattr(current_user, 'school_id', None)
        
        ems_sync_result = await ems_sync.sync_summary(
            gurukul_id=new_summary.id,
            student_email=current_user.email,
            school_id=school_id,
            title=summary_in.title,
            content=summary_in.content,
            source=summary_in.source or "manual",
            source_type=summary_in.source_type or "text"
        )
        
        if ems_sync_result:
            # Store EMS sync ID in metadata if needed
            new_summary.metadata_ = new_summary.metadata_ or {}
            new_summary.metadata_["ems_sync_id"] = ems_sync_result.get("id")
            db.commit()
            logger.info(f"Synced summary {new_summary.id} to EMS")
    except Exception as e:
        logger.error(f"Failed to sync summary {new_summary.id} to EMS: {str(e)}")
        # Don't fail the request if sync fails
    
    return {"message": "Summary saved successfully", "id": new_summary.id}


@router.get("/summaries")
async def get_user_summaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all summaries for the current user"""
    summaries = db.query(DBSummary).filter(
        DBSummary.user_id == current_user.id
    ).order_by(DBSummary.created_at.desc()).all()
    
    return [{
        "id": s.id,
        "title": s.title,
        "content": s.content,
        "source": s.source,
        "source_type": s.source_type,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in summaries]


@router.get("/subject-data")
async def get_user_subject_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all subject explorer data for the current user"""
    subject_data = db.query(SubjectData).filter(
        SubjectData.user_id == current_user.id
    ).order_by(SubjectData.created_at.desc()).all()
    
    return [{
        "id": s.id,
        "subject": s.subject,
        "topic": s.topic,
        "notes": s.notes,
        "provider": s.provider,
        "youtube_recommendations": s.youtube_recommendations or [],
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in subject_data]
