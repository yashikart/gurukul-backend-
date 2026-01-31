"""
PRANA Packet Models

Database models for storing PRANA packets from the frontend.
Used by the bucket layer to store packets before Karma Tracker processes them.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class PranaPacket(Base):
    """
    PRANA Packet - Stores packets from PRANA system before Karma Tracker processes them.
    
    Each packet represents 5 seconds of user activity data.
    """
    __tablename__ = "prana_packets"

    # Primary key
    packet_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    
    # User identification
    user_id = Column(String, nullable=True, index=True)  # Gurukul user ID
    employee_id = Column(String, nullable=True, index=True)  # EMS employee ID (legacy)
    session_id = Column(String, nullable=True, index=True)
    lesson_id = Column(String, nullable=True)
    
    # System context
    system_type = Column(String, nullable=True)  # "gurukul" or "ems"
    role = Column(String, nullable=True)  # "student" or "employee"
    
    # Timestamps
    client_timestamp = Column(DateTime(timezone=True), nullable=False)  # When PRANA created the packet
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # When bucket received it
    processed_at = Column(DateTime(timezone=True), nullable=True)  # When Karma Tracker processed it
    
    # Cognitive state
    cognitive_state = Column(String, nullable=True)  # Unified states: ON_TASK, THINKING, IDLE, etc.
    state = Column(String, nullable=True)  # Legacy state field
    
    # Time accounting (must sum to 5.0)
    active_seconds = Column(Float, nullable=False)
    idle_seconds = Column(Float, nullable=False)
    away_seconds = Column(Float, nullable=False)
    
    # Scores
    focus_score = Column(Float, nullable=True)  # 0-100
    integrity_score = Column(Float, nullable=True)  # 0-1 (legacy)
    
    # Raw signals (stored as JSON)
    raw_signals = Column(JSON, nullable=False, default=dict)
    
    # Processing status
    processed_by_karma = Column(Boolean, default=False, nullable=False, index=True)
    karma_actions = Column(JSON, nullable=True, default=list)  # List of karma actions generated from this packet
    processing_error = Column(Text, nullable=True)  # Error message if processing failed
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_processed', 'user_id', 'processed_by_karma'),
        Index('idx_received_at', 'received_at'),
        Index('idx_processed_at', 'processed_at'),
    )

