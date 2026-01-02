
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# --- EMS & Governance Models ---

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # INSTITUTION, FAMILY
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False) # ADMIN, TEACHER, PARENT, STUDENT
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")
    profile = relationship("Profile", back_populates="user", uselist=False)
    summaries = relationship("Summary", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")
    reflections = relationship("Reflection", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Generic JSON bag for Student/Teacher specific data
    # Student: grade, subjects, learning_style
    # Teacher: subjects_taught, qualifications
    data = Column(JSON, default={})
    
    user = relationship("User", back_populates="profile")

# --- Soul & Pedagogy Models ---

class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    mood_score = Column(Integer, nullable=True) # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reflections")

# --- Learning Models ---

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # Optional for now if guest access allowed
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata_ = Column("metadata", JSON, default={}) # metadata is reserved in SQLAlchemy Base

    user = relationship("User", back_populates="summaries")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    question_type = Column(String, default="conceptual")
    days_until_review = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="flashcards")
