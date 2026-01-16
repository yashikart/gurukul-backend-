from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.dependencies import get_current_parent
from app.models import (
    User, UserRole, Class, ClassStudent, Lesson, Lecture, 
    TimetableSlot, Subject, Announcement, Attendance, StudentParent
)
from app.schemas import (
    ClassResponse, LessonResponse, 
    TimetableSlotResponse, AnnouncementResponse, AttendanceResponse
)
from pydantic import BaseModel
from datetime import date, datetime

router = APIRouter(prefix="/parent", tags=["parent"])


# ==================== PARENT DASHBOARD STATS ====================

class ParentDashboardStats(BaseModel):
    total_children: int
    total_classes: int
    total_lessons: int
    recent_announcements: int


@router.get("/dashboard/stats", response_model=ParentDashboardStats)
def get_parent_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_parent)
):
    """Get parent dashboard statistics."""
    parent_id = current_user.id
    school_id = current_user.school_id
    
    # Get children (students linked to this parent)
    parent_links = db.query(StudentParent).filter(
        StudentParent.parent_id == parent_id
    ).all()
    
    student_ids = [link.student_id for link in parent_links]
    total_children = len(student_ids)
    
    # Get classes for all children
    total_classes = 0
    total_lessons = 0
    if student_ids:
        enrollments = db.query(ClassStudent).filter(
            ClassStudent.student_id.in_(student_ids)
        ).all()
        class_ids = list(set([e.class_id for e in enrollments]))
        total_classes = len(class_ids)
        
        if class_ids:
            all_lessons = db.query(Lesson).filter(
                Lesson.class_id.in_(class_ids),
                Lesson.school_id == school_id
            ).all()
            total_lessons = len(all_lessons)
    
    # Count recent announcements (from last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_announcements = db.query(Announcement).filter(
        Announcement.school_id == school_id,
        or_(
            Announcement.target_audience == "PARENTS",
            Announcement.target_audience == "EVERYONE"
        ),
        Announcement.published_at >= week_ago
    ).count()
    
    return ParentDashboardStats(
        total_children=total_children,
        total_classes=total_classes,
        total_lessons=total_lessons,
        recent_announcements=recent_announcements
    )


# ==================== PARENT'S CHILDREN ====================

class ChildResponse(BaseModel):
    id: int
    name: str
    email: str
    grade: Optional[str] = None
    classes: List[ClassResponse] = []
    
    class Config:
        from_attributes = True


@router.get("/children", response_model=List[ChildResponse])
def get_my_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_parent)
):
    """Get all children (students) linked to this parent."""
    parent_id = current_user.id
    school_id = current_user.school_id
    
    # Get parent-student links
    parent_links = db.query(StudentParent).filter(
        StudentParent.parent_id == parent_id
    ).all()
    
    student_ids = [link.student_id for link in parent_links]
    if not student_ids:
        return []
    
    # Get students
    students = db.query(User).filter(
        User.id.in_(student_ids),
        User.role == UserRole.STUDENT,
        User.school_id == school_id
    ).all()
    
    result = []
    for student in students:
        # Get classes for this student
        enrollments = db.query(ClassStudent).filter(
            ClassStudent.student_id == student.id
        ).all()
        class_ids = [e.class_id for e in enrollments]
        
        classes = db.query(Class).filter(
            Class.id.in_(class_ids),
            Class.school_id == school_id
        ).all()
        
        # Build ClassResponse for each class
        class_responses = []
        for cls in classes:
            subject = db.query(Subject).filter(Subject.id == cls.subject_id).first()
            teacher = db.query(User).filter(User.id == cls.teacher_id).first()
            
            class_responses.append(ClassResponse(
                id=cls.id,
                name=cls.name,
                grade=cls.grade,
                subject_id=cls.subject_id,
                teacher_id=cls.teacher_id,
                school_id=cls.school_id,
                academic_year=cls.academic_year,
                subject_name=subject.name if subject else None,
                teacher_name=teacher.name if teacher else None
            ))
        
        result.append(ChildResponse(
            id=student.id,
            name=student.name,
            email=student.email,
            grade=student.grade,
            classes=class_responses
        ))
    
    return result


# ==================== PARENT'S CHILDREN GRADES ====================

@router.get("/grades")
def get_my_children_grades(
    child_id: Optional[int] = Query(None, description="Filter by child/student ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_parent)
):
    """Get grades for parent's children."""
    parent_id = current_user.id
    school_id = current_user.school_id
    
    # Get children linked to this parent
    parent_links = db.query(StudentParent).filter(
        StudentParent.parent_id == parent_id
    ).all()
    
    student_ids = [link.student_id for link in parent_links]
    if not student_ids:
        return []
    
    # Filter by child_id if provided
    if child_id:
        if child_id not in student_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This student is not linked to your account"
            )
        student_ids = [child_id]
    
    # TODO: Implement grades model and return actual grades
    # For now, return empty list
    return []


# ==================== PARENT'S CHILDREN ATTENDANCE ====================

@router.get("/attendance", response_model=List[AttendanceResponse])
def get_my_children_attendance(
    child_id: Optional[int] = Query(None, description="Filter by child/student ID"),
    attendance_date: Optional[date] = Query(None, description="Filter by date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_parent)
):
    """Get attendance records for parent's children."""
    parent_id = current_user.id
    school_id = current_user.school_id
    
    # Get children linked to this parent
    parent_links = db.query(StudentParent).filter(
        StudentParent.parent_id == parent_id
    ).all()
    
    student_ids = [link.student_id for link in parent_links]
    if not student_ids:
        return []
    
    # Filter by child_id if provided
    if child_id:
        if child_id not in student_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This student is not linked to your account"
            )
        student_ids = [child_id]
    
    # Get attendance records
    query = db.query(Attendance).filter(
        Attendance.student_id.in_(student_ids),
        Attendance.school_id == school_id
    )
    
    if attendance_date:
        query = query.filter(Attendance.attendance_date == attendance_date)
    
    attendance_records = query.order_by(Attendance.attendance_date.desc()).all()
    
    result = []
    for record in attendance_records:
        class_obj = db.query(Class).filter(Class.id == record.class_id).first()
        
        result.append(AttendanceResponse(
            id=record.id,
            student_id=record.student_id,
            class_id=record.class_id,
            teacher_id=record.teacher_id,
            school_id=record.school_id,
            attendance_date=record.attendance_date,
            status=record.status,
            remarks=record.remarks,
            created_at=record.created_at,
            class_name=class_obj.name if class_obj else None
        ))
    
    return result


# ==================== PARENT'S ANNOUNCEMENTS ====================

@router.get("/announcements", response_model=List[AnnouncementResponse])
def get_my_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_parent)
):
    """Get announcements targeted to parents."""
    school_id = current_user.school_id
    
    announcements = db.query(Announcement).filter(
        Announcement.school_id == school_id,
        or_(
            Announcement.target_audience == "PARENTS",
            Announcement.target_audience == "EVERYONE"
        )
    ).order_by(Announcement.published_at.desc()).all()
    
    result = []
    for ann in announcements:
        creator = db.query(User).filter(User.id == ann.created_by).first()
        
        result.append(AnnouncementResponse(
            id=ann.id,
            title=ann.title,
            content=ann.content,
            target_audience=ann.target_audience,
            school_id=ann.school_id,
            published_at=ann.published_at,
            created_by=ann.created_by,
            created_by_name=creator.name if creator else None
        ))
    
    return result

