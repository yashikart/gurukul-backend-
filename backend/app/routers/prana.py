from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.prana_runtime import prana_runtime


class PranaIngestRequest(BaseModel):
    submission_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    timestamp: str
    payload: Dict[str, Any]
    source_system: str = "gurukul"

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: str) -> str:
        from datetime import datetime

        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("timestamp must be a valid ISO-8601 string") from exc
        return value


router = APIRouter()


@router.post("/prana/ingest")
def ingest_prana_event(request: PranaIngestRequest, db: Session = Depends(get_db)):
    try:
        result = prana_runtime.ingest_event(
            db,
            submission_id=request.submission_id,
            event_type=request.event_type,
            timestamp=request.timestamp,
            payload=request.payload,
            source_system=request.source_system,
        )
        return {"status": "success", **result}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to ingest PRANA event: {exc}") from exc


@router.get("/prana/events")
def get_prana_events(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return prana_runtime.get_recent_events(db, limit=limit)


@router.get("/prana/vitality")
def get_prana_vitality(db: Session = Depends(get_db)):
    return prana_runtime.get_vitality_summary(db)


@router.post("/prana/verify")
def verify_prana_event(event_id: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        if event_id:
            return prana_runtime.verify_event(db, event_id)
        return prana_runtime.verify_all(db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to verify PRANA event(s): {exc}") from exc
