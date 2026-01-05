from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.core.security import get_password_hash
from app.models.all_models import User, Tenant, Cohort, Flashcard, Summary, Reflection, StudentProgress
from app.schemas.ems import TenantCreate, TenantResponse, UserCreateAdmin, UserResponse, CohortCreate, CohortResponse
import uuid

router = APIRouter()

# --- Admin Endpoints ---

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Create a new School/Institution (Tenant)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admins can create tenants")
    
    new_tenant = Tenant(
        name=tenant.name,
        type=tenant.type
    )
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    return new_tenant

@router.post("/cohorts", response_model=CohortResponse, status_code=status.HTTP_201_CREATED)
async def create_cohort(
    cohort: CohortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Create a Cohort (Class) within a Tenant"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admins can create cohorts")
    
    # Verify tenant exists
    if not db.query(Tenant).filter(Tenant.id == cohort.tenant_id).first():
        raise HTTPException(status_code=404, detail="Tenant not found")

    new_cohort = Cohort(
        name=cohort.name,
        tenant_id=cohort.tenant_id
    )
    db.add(new_cohort)
    db.commit()
    db.refresh(new_cohort)
    return new_cohort

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_within_tenant(
    user_in: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Add a User (Teacher/Student) to a Tenant"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admins can create users")

    # Check if email exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)
    
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=user_in.role.upper(), # Ensure uppercase
        tenant_id=user_in.tenant_id,
        cohort_id=user_in.cohort_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=List[UserResponse])
async def get_users_in_tenant(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: List all users in the tenant"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admins can list users")
    
    # Filter by user's tenant
    users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    return users

# --- Teacher Endpoints ---

@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Teacher: View a specific Student's progress"""
    # Authorization: Admin or Teacher (in same tenant)
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == "STUDENT":
        # Student can only view their own
        if current_user.id != student_id:
             raise HTTPException(status_code=403, detail="Cannot view other student's progress")
    elif current_user.role == "TEACHER":
         # Check tenant match
         if current_user.tenant_id and current_user.tenant_id != student.tenant_id:
             raise HTTPException(status_code=403, detail="Cannot view student from another institution")
    
    # Calculate Stats
    topics_count = db.query(Summary).filter(Summary.user_id == student_id).count()
    flashcards_count = db.query(Flashcard).filter(Flashcard.user_id == student_id).count()
    completed_milestones = db.query(StudentProgress).filter(
        StudentProgress.user_id == student_id, 
        StudentProgress.status == "COMPLETED"
    ).count()

    return {
        "studentName": student.full_name,
        "topicsStudied": topics_count,
        "flashcardsCreated": flashcards_count,
        "milestonesCompleted": completed_milestones,
        "lastActivity": "Today" # Placeholder
    }

# --- Dashboard Hooks (Restored for Frontend Compatibility) ---
# --- Dashboard Hooks (Restored for Frontend Compatibility) ---
@router.get("/dashboard/stats")
async def get_my_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get MY progress (Student View)"""
    return await get_student_progress(current_user.id, db, current_user)

@router.get("/admin/stats")
async def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get System Stats for Admin Dashboard"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only Admins can view system stats")
        
    # Scope to tenant if tenant_id is set, else global?
    # Assuming Admin sees stats for their Tenant.
    
    base_query = db.query(User)
    if current_user.tenant_id:
        base_query = base_query.filter(User.tenant_id == current_user.tenant_id)
        
    total_users = base_query.count()
    active_users = base_query.filter(User.is_active == True).count()
    total_teachers = base_query.filter(User.role == "TEACHER").count()
    total_students = base_query.filter(User.role == "STUDENT").count()
    total_parents = base_query.filter(User.role == "PARENT").count()
    
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalTeachers": total_teachers,
        "totalStudents": total_students,
        "totalParents": total_parents,
        "systemHealth": "Healthy",
        "apiStatus": "Operational"
    }


