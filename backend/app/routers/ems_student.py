"""
EMS Student Integration Router
Proxy endpoints for student features from EMS System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User
from app.services.ems_client import ems_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ems/student", tags=["EMS Student Integration"])


class EMSTokenRequest(BaseModel):
    email: EmailStr
    password: str


async def get_ems_token(
    ems_token: Optional[str] = Header(None, alias="X-EMS-Token"),
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Get EMS token from header or generate from user credentials
    For Phase 1: Token is passed from frontend
    For Phase 3: We'll auto-generate/store tokens
    """
    if not ems_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="EMS token required. Please authenticate with EMS first."
        )
    return ems_token


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student dashboard statistics from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        stats = await ems_client.get_student_dashboard_stats(token)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        )


@router.get("/classes")
async def get_classes(
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student's enrolled classes from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        classes = await ems_client.get_student_classes(token)
        return classes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch classes: {str(e)}"
        )


@router.get("/lessons")
async def get_lessons(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student's lessons from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        lessons = await ems_client.get_student_lessons(token, class_id)
        return lessons
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch lessons: {str(e)}"
        )


@router.get("/timetable")
async def get_timetable(
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student's timetable/schedule from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        timetable = await ems_client.get_student_timetable(token)
        return timetable
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch timetable: {str(e)}"
        )


@router.get("/announcements")
async def get_announcements(
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student announcements from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        announcements = await ems_client.get_student_announcements(token)
        return announcements
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch announcements: {str(e)}"
        )


@router.get("/attendance")
async def get_attendance(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    attendance_date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student's attendance records from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        attendance = await ems_client.get_student_attendance(token, class_id, attendance_date)
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch attendance: {str(e)}"
        )


@router.get("/teachers")
async def get_teachers(
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student's teachers from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        teachers = await ems_client.get_student_teachers(token)
        return teachers
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch teachers: {str(e)}"
        )


@router.get("/grades")
async def get_grades(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    token: str = Depends(get_ems_token),
    current_user: User = Depends(get_current_user)
):
    """Get student's grades from EMS"""
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    try:
        grades = await ems_client.get_student_grades(token, class_id)
        return grades
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch grades: {str(e)}"
        )


@router.post("/auth/ems-token")
async def get_ems_token_from_credentials(
    credentials: EMSTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Authenticate with EMS using user credentials and return EMS token
    This is a helper endpoint for Phase 1
    In Phase 3, we'll auto-create EMS accounts and store tokens
    """
    if current_user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Verify email matches current user
    if current_user.email != credentials.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email must match your Gurukul account"
        )
    
    # Strip whitespace from password (common issue)
    password_cleaned = credentials.password.strip()
    
    try:
        logger.info(f"Student {current_user.email} attempting EMS authentication with email: {credentials.email}")
        logger.debug(f"Password length: {len(password_cleaned)}, First 2 chars: {password_cleaned[:2] if len(password_cleaned) >= 2 else 'N/A'}")
        token_response = await ems_client.login(credentials.email, password_cleaned)
        
        if not token_response or "access_token" not in token_response:
            logger.error(f"EMS login returned invalid response: {token_response}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="EMS authentication returned invalid response"
            )
        
        logger.info(f"EMS authentication successful for student {current_user.email}")
        return {
            "ems_token": token_response.get("access_token"),
            "token_type": token_response.get("token_type", "bearer"),
            "message": "EMS authentication successful"
        }
    except HTTPException as e:
        logger.error(f"EMS authentication HTTPException for {credentials.email}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"EMS authentication exception for {credentials.email}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"EMS authentication failed: {str(e)}"
        )


@router.get("/health")
async def check_ems_health():
    """Check if EMS System is reachable"""
    try:
        health = await ems_client.health_check()
        return {
            "ems_status": "reachable",
            "ems_response": health
        }
    except Exception as e:
        return {
            "ems_status": "unreachable",
            "error": str(e)
        }

