
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User, Reflection as DBReflection
from pydantic import BaseModel

router = APIRouter()

class ReflectionCreate(BaseModel):
    content: str
    mood_score: int

class ReflectionResponse(BaseModel):
    id: str
    content: str
    mood_score: int
    created_at: str

@router.post("/", response_model=ReflectionResponse)
async def create_reflection(
    reflection: ReflectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a learning reflection or mood check-in (Soul Alignment)"""
    new_reflection = DBReflection(
        user_id=current_user.id,
        content=reflection.content,
        mood_score=reflection.mood_score
    )
    db.add(new_reflection)
    db.commit()
    db.refresh(new_reflection)
    
    return ReflectionResponse(
        id=new_reflection.id,
        content=new_reflection.content,
        mood_score=new_reflection.mood_score or 0,
        created_at=str(new_reflection.created_at)
    )

@router.get("/", response_model=List[ReflectionResponse])
async def get_my_reflections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get learning journey history"""
    refs = db.query(DBReflection).filter(DBReflection.user_id == current_user.id).all()
    return [
        ReflectionResponse(
            id=r.id,
            content=r.content,
            mood_score=r.mood_score or 0,
            created_at=str(r.created_at)
        ) for r in refs
    ]
