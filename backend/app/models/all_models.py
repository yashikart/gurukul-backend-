
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, JSON, Enum
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
    cohorts = relationship("Cohort", back_populates="tenant")

class Cohort(Base):
    __tablename__ = "cohorts"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False) # e.g. "Grade 10-A"
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="cohorts")
    users = relationship("User", back_populates="cohort")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False) # ADMIN, TEACHER, PARENT, STUDENT
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True)
    cohort_id = Column(String, ForeignKey("cohorts.id"), nullable=True) # For Students
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="users")
    cohort = relationship("Cohort", back_populates="users")
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

class LearningTrack(Base):
    __tablename__ = "learning_tracks"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True) # Optional: Global vs Tenant specific
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    milestones = relationship("Milestone", back_populates="track")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(String, primary_key=True, default=generate_uuid)
    track_id = Column(String, ForeignKey("learning_tracks.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    
    track = relationship("LearningTrack", back_populates="milestones")
    student_progress = relationship("StudentProgress", back_populates="milestone")

class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    milestone_id = Column(String, ForeignKey("milestones.id"), nullable=False)
    status = Column(String, default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED
    evidence = Column(Text, nullable=True) # Link to artifact or summary
    reflection_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User") # Simplify relationship for now
    milestone = relationship("Milestone", back_populates="student_progress")

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
