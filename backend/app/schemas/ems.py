from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class TenantCreate(BaseModel):
    name: str # School Name
    type: str = "INSTITUTION" # INSTITUTION or FAMILY

class TenantResponse(TenantCreate):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CohortCreate(BaseModel):
    name: str # e.g. "Grade 10-A"
    tenant_id: str

class CohortResponse(CohortCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreateAdmin(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str # ADMIN, TEACHER, STUDENT, PARENT
    tenant_id: str
    cohort_id: Optional[str] = None # For Students

class UserUpdateAdmin(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    tenant_id: Optional[str]
    cohort_id: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
