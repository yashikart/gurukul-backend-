from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
from app.services.llm import call_groq_api, call_ollama_api
from app.core.config import settings

router = APIRouter()

# --- Schemas ---

class EduMentorRequest(BaseModel):
    subject: str
    topic: str
    include_wikipedia: bool = False
    use_knowledge_store: bool = False
    use_orchestration: bool = False

class ExpenseCategory(BaseModel):
    name: str
    amount: float

class FinancialRequest(BaseModel):
    name: str
    monthly_income: float
    monthly_expenses: float
    expense_categories: List[ExpenseCategory]
    financial_goal: str
    financial_type: str
    risk_level: str

class WellnessRequest(BaseModel):
    emotional_wellness_score: int
    financial_wellness_score: int
    current_mood_score: int
    stress_level: int
    concerns: Optional[str] = None

class TTSAgentRequest(BaseModel):
    text: str
    language: str = "en"

# --- Endpoints ---

@router.post("/tts")
async def agent_generate_tts(request: TTSAgentRequest):
    """
    Unified Vaani TTS Generation endpoint for agents.
    Includes caching (MongoDB) and telemetry (insightflow_logs).
    """
    from app.services.vaani_client import vaani_client
    from app.core.karma_database import get_db
    import datetime

    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    text_hash = vaani_client.generate_hash(text, request.language)
    
    try:
        db = None
        try:
            db = get_db()
        except Exception as db_err:
            print(f"Agent TTS: MongoDB not available, proceeding without cache: {db_err}")

        # 1. Caching Check (skipped if DB is None)
        if db is not None:
            try:
                cached = db.tts_cache.find_one({"text_hash": text_hash})
                if cached:
                    return {
                        "status": "success",
                        "audio_id": text_hash,
                        "cached": True,
                        "audio_url": f"/api/v1/agent/download-audio?audio_id={text_hash}"
                    }
            except Exception as cache_err:
                print(f"Agent TTS Cache check failed: {cache_err}")

        # 2. Generation
        result = await vaani_client.generate_tts(text, request.language)
        
        if result["status"] == "success":
            # 3. Store in Cache (if DB is available)
            if db is not None:
                try:
                    db.tts_cache.insert_one({
                        "text_hash": text_hash,
                        "text": text,
                        "language": request.language,
                        "created_at": datetime.datetime.now(datetime.timezone.utc),
                        "audio_data": result["audio_data"],
                        "media_type": result.get("media_type", "audio/wav")
                    })

                    # 4. Telemetry (insightflow_logs)
                    db.insightflow_logs.insert_one({
                        "event": "tts_generation",
                        "text": text[:100],
                        "language": request.language,
                        "audio_id": text_hash,
                        "timestamp": datetime.datetime.now(datetime.timezone.utc),
                        "source": "vaani_sentinel"
                    })
                except Exception as store_err:
                    print(f"Agent TTS Cache storage failed: {store_err}")

            return {
                "status": "success",
                "audio_id": text_hash,
                "cached": False,
                "audio_url": f"/api/v1/agent/download-audio?audio_id={text_hash}"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Generation failed"))

    except HTTPException:
        raise
    except Exception as e:
        print(f"Agent TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-audio")
async def download_agent_audio(audio_id: str):
    """
    Retrieve audio from tts_cache.
    """
    from app.core.karma_database import get_db
    from fastapi.responses import Response

    try:
        db = get_db()
        cached = db.tts_cache.find_one({"text_hash": audio_id})
        
        if not cached:
            raise HTTPException(status_code=404, detail="Audio not found")

        return Response(
            content=cached["audio_data"],
            media_type=cached.get("media_type", "audio/wav"),
            headers={
                "Content-Disposition": f"attachment; filename={audio_id}.{'mp3' if 'mpeg' in cached.get('media_type', '') else 'wav'}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
