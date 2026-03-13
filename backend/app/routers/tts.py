from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    language: str = "en"  # Language code (e.g., 'en', 'es', 'fr', 'de', etc.)

@router.get("/voices")
async def get_available_voices():
    """
    Get list of available TTS voices on the system
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        if voices:
            for voice in voices:
                voice_list.append({
                    "name": voice.name,
                    "id": voice.id,
                    "languages": voice.languages if hasattr(voice, 'languages') else [],
                    "gender": voice.gender if hasattr(voice, 'gender') else "Unknown",
                    "age": voice.age if hasattr(voice, 'age') else "Unknown"
                })
        
        return {
            "voices": voice_list,
            "total": len(voice_list)
        }
    except Exception as e:
        print(f"[TTS] Error getting voices: {e}")
        return {"voices": [], "total": 0, "error": str(e)}

@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return audio file (Google TTS)
    """
    try:
        from app.services.tts_core_functions import text_to_speech_stream
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Log the language being used
        print(f"[Vaani] Standard API - Request received - Language: {request.language}")
        
        # Use our sovereign engine (redirected inside text_to_speech_stream)
        audio_data = await text_to_speech_stream(request.text, language=request.language, use_google_tts=True)
        
        # Vaani engine returns WAV by default in our current setup
        media_type = "audio/wav"
        file_ext = "wav"
        
        # Return audio file
        return Response(
            content=audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=vaani_speech.{file_ext}"
            }
        )
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )

def _gtts_lang_code(lang: str) -> str:
    """Map frontend language code to gTTS lang code. gTTS uses ISO 639-1 (e.g. zh-cn, pt-br)."""
    if not lang or not lang.strip():
        return "en"
    lang = lang.strip().lower()
    # gTTS uses zh-cn / zh-tw for Chinese
    if lang in ("zh", "zh-cn", "zh_cn"):
        return "zh-cn"
    if lang == "zh-tw":
        return "zh-tw"
    # Other codes (en, hi, ja, ko, ar, fr, es, etc.) are used as-is by gTTS
    return lang if len(lang) >= 2 else "en"


@router.post("/vaani")
async def vaani_text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Vaani TTS (gTTS).
    Translates text to the target language first (like Google TTS path), then speaks
    so you get actual Hindi/Japanese/etc. speech, not English in an accent.
    """
    try:
        from app.services.tts_core_functions import text_to_speech_stream
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        print(f"[Vaani] Sovereign Endpoint - Request received - Language: {request.language}")
        
        # Use our sovereign engine (redirected inside text_to_speech_stream)
        audio_data = await text_to_speech_stream(request.text, language=request.language, use_google_tts=True)
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=vaani_sovereign_speech.wav"
            }
        )
    
    except Exception as e:
        print(f"[Vaani TTS] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech with Vaani TTS: {str(e)}"
        )
