"""
Manual EMS Sync Router
Allows manual syncing of existing content from Gurukul to EMS
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User, Summary, Flashcard, TestResult, SubjectData
from app.services.ems_sync import ems_sync
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ems/sync", tags=["EMS Manual Sync"])


@router.post("/all-content")
async def sync_all_user_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually sync all existing content for the current user to EMS
    This is useful for syncing content that was created before auto-sync was implemented
    """
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can sync their content"
        )
    
    # Log the student email being used for debugging
    logger.info(f"Starting sync for student: {current_user.email} (ID: {current_user.id})")
    
    # Get user's school_id if available (from tenant or other source)
    school_id = None
    if hasattr(current_user, 'school_id') and current_user.school_id:
        school_id = current_user.school_id
    elif hasattr(current_user, 'tenant_id'):
        # If using tenant system, you might need to get school_id from tenant
        # For now, we'll use None and let EMS use the student's school_id
        school_id = None
    
    results = {
        "summaries": {"synced": 0, "failed": 0, "errors": []},
        "flashcards": {"synced": 0, "failed": 0, "errors": []},
        "test_results": {"synced": 0, "failed": 0, "errors": []},
        "subject_data": {"synced": 0, "failed": 0, "errors": []}
    }
    
    # Sync Summaries
    summaries = db.query(Summary).filter(
        Summary.user_id == current_user.id
    ).all()
    
    for summary in summaries:
        try:
            sync_result = await ems_sync.sync_summary(
                gurukul_id=summary.id,
                student_email=current_user.email,
                school_id=school_id,
                title=summary.title,
                content=summary.content,
                source=summary.source,
                source_type=summary.source_type or "text",
                extra_metadata={}
            )
            if sync_result:
                results["summaries"]["synced"] += 1
            else:
                results["summaries"]["failed"] += 1
                results["summaries"]["errors"].append(f"Summary {summary.id}: Sync returned None (check EMS logs)")
        except HTTPException as e:
            error_msg = f"HTTP {e.status_code}: {e.detail}"
            logger.error(f"Failed to sync summary {summary.id}: {error_msg}")
            results["summaries"]["failed"] += 1
            results["summaries"]["errors"].append(f"Summary {summary.id}: {error_msg}")
        except Exception as e:
            logger.error(f"Failed to sync summary {summary.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            results["summaries"]["failed"] += 1
            results["summaries"]["errors"].append(f"Summary {summary.id}: {str(e)}")
    
    # Sync Flashcards
    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id
    ).all()
    
    for flashcard in flashcards:
        try:
            sync_result = await ems_sync.sync_flashcard(
                gurukul_id=flashcard.id,
                student_email=current_user.email,
                school_id=school_id,
                question=flashcard.question,
                answer=flashcard.answer,
                question_type=flashcard.question_type or "conceptual",
                days_until_review=flashcard.days_until_review or 0,
                confidence=flashcard.confidence or 0.0
            )
            if sync_result:
                results["flashcards"]["synced"] += 1
            else:
                results["flashcards"]["failed"] += 1
                results["flashcards"]["errors"].append(f"Flashcard {flashcard.id}: Sync returned None (check EMS logs)")
        except HTTPException as e:
            error_msg = f"HTTP {e.status_code}: {e.detail}"
            logger.error(f"Failed to sync flashcard {flashcard.id}: {error_msg}")
            results["flashcards"]["failed"] += 1
            results["flashcards"]["errors"].append(f"Flashcard {flashcard.id}: {error_msg}")
        except Exception as e:
            logger.error(f"Failed to sync flashcard {flashcard.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            results["flashcards"]["failed"] += 1
            results["flashcards"]["errors"].append(f"Flashcard {flashcard.id}: {str(e)}")
    
    # Sync Test Results
    test_results = db.query(TestResult).filter(
        TestResult.user_id == current_user.id
    ).all()
    
    for test_result in test_results:
        try:
            sync_result = await ems_sync.sync_test_result(
                gurukul_id=test_result.id,
                student_email=current_user.email,
                school_id=school_id,
                subject=test_result.subject,
                topic=test_result.topic,
                difficulty=test_result.difficulty or "medium",
                num_questions=test_result.num_questions or test_result.total_questions,
                questions=test_result.questions or {},
                user_answers=test_result.user_answers or {},
                score=test_result.score,
                total_questions=test_result.total_questions,
                percentage=test_result.percentage,
                time_taken=getattr(test_result, 'time_taken', None)
            )
            if sync_result:
                results["test_results"]["synced"] += 1
            else:
                results["test_results"]["failed"] += 1
                results["test_results"]["errors"].append(f"Test {test_result.id}: Sync returned None (check EMS logs)")
        except HTTPException as e:
            error_msg = f"HTTP {e.status_code}: {e.detail}"
            logger.error(f"Failed to sync test result {test_result.id}: {error_msg}")
            results["test_results"]["failed"] += 1
            results["test_results"]["errors"].append(f"Test {test_result.id}: {error_msg}")
        except Exception as e:
            logger.error(f"Failed to sync test result {test_result.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            results["test_results"]["failed"] += 1
            results["test_results"]["errors"].append(f"Test {test_result.id}: {str(e)}")
    
    # Sync Subject Data
    subject_data_list = db.query(SubjectData).filter(
        SubjectData.user_id == current_user.id
    ).all()
    
    for subject_data in subject_data_list:
        try:
            sync_result = await ems_sync.sync_subject_data(
                gurukul_id=subject_data.id,
                student_email=current_user.email,
                school_id=school_id,
                subject=subject_data.subject,
                topic=subject_data.topic,
                notes=subject_data.notes,
                provider=subject_data.provider,
                youtube_recommendations=subject_data.youtube_recommendations or []
            )
            if sync_result:
                results["subject_data"]["synced"] += 1
            else:
                results["subject_data"]["failed"] += 1
                results["subject_data"]["errors"].append(f"Subject data {subject_data.id}: Sync returned None (check EMS logs)")
        except HTTPException as e:
            error_msg = f"HTTP {e.status_code}: {e.detail}"
            logger.error(f"Failed to sync subject data {subject_data.id}: {error_msg}")
            results["subject_data"]["failed"] += 1
            results["subject_data"]["errors"].append(f"Subject data {subject_data.id}: {error_msg}")
        except Exception as e:
            logger.error(f"Failed to sync subject data {subject_data.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            results["subject_data"]["failed"] += 1
            results["subject_data"]["errors"].append(f"Subject data {subject_data.id}: {str(e)}")
    
    total_synced = (
        results["summaries"]["synced"] +
        results["flashcards"]["synced"] +
        results["test_results"]["synced"] +
        results["subject_data"]["synced"]
    )
    
    total_failed = (
        results["summaries"]["failed"] +
        results["flashcards"]["failed"] +
        results["test_results"]["failed"] +
        results["subject_data"]["failed"]
    )
    
    return {
        "message": f"Sync completed. {total_synced} items synced, {total_failed} failed.",
        "results": results,
        "total_synced": total_synced,
        "total_failed": total_failed
    }

