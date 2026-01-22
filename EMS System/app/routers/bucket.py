from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Literal, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PranaPacket


class PranaPacketIn(BaseModel):
    employee_id: str
    task_id: Optional[str] = None
    timestamp: str
    state: Literal["WORKING", "IDLE", "AWAY", "DISTRACTED", "FAKING"]
    active_seconds: float
    idle_seconds: float
    away_seconds: float
    integrity_score: float = Field(..., ge=0.0, le=1.0)
    raw_signals: Dict[str, Any]

    @validator("timestamp")
    def validate_timestamp(cls, v: str) -> str:
        try:
            # Ensure it parses as ISO-8601
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("timestamp must be a valid ISO-8601 string")
        return v

    @validator("raw_signals")
    def validate_raw_signals(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("raw_signals must be an object")
        return v

    @validator("active_seconds", "idle_seconds", "away_seconds")
    def non_negative_seconds(cls, v: float) -> float:
        if v < 0:
            raise ValueError("time values must be non-negative")
        return v

    @validator("*")
    def validate_total_window(cls, v, values):
        # This will run for each field; enforce total window once we have all three
        active = values.get("active_seconds")
        idle = values.get("idle_seconds")
        away = values.get("away_seconds")
        if active is not None and idle is not None and away is not None:
            if active + idle + away > 10:
                raise ValueError("Sum of active_seconds + idle_seconds + away_seconds must be <= 10")
        return v


class PranaPacketResponse(BaseModel):
    status: str
    packet_id: str
    received_at: str


class PranaPacketError(BaseModel):
    status: str
    reason: str
    details: str


router = APIRouter()


@router.post(
    "/bucket/prana/ingest",
    response_model=PranaPacketResponse,
    responses={
        400: {"model": PranaPacketError},
    },
)
def ingest_prana_packet(payload: PranaPacketIn, db: Session = Depends(get_db)):
    """
    BHIV Bucket PRANA ingest endpoint.
    - Validates a single PRANA-E packet
    - Appends it as an immutable ledger entry
    """
    try:
        client_ts = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
    except Exception:
        # This should normally be caught by the validator, but we keep this for absolute safety
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "rejected",
                "reason": "validation_error",
                "details": "Invalid timestamp format",
            },
        )

    packet_id = str(uuid4())
    received_at = datetime.now(timezone.utc)

    record = PranaPacket(
        packet_id=packet_id,
        employee_id=payload.employee_id,
        task_id=payload.task_id,
        state=payload.state,
        integrity_score=payload.integrity_score,
        active_seconds=payload.active_seconds,
        idle_seconds=payload.idle_seconds,
        away_seconds=payload.away_seconds,
        raw_signals=payload.raw_signals,
        client_timestamp=client_ts,
        received_at=received_at,
    )

    db.add(record)
    db.commit()

    return PranaPacketResponse(
        status="ingested",
        packet_id=packet_id,
        received_at=received_at.isoformat(),
    )


