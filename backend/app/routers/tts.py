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
    Convert text to speech and return audio file
    """
    try:
        from app.services.tts_core_functions import text_to_speech_stream
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Log the language being used
        print(f"[TTS] Request received - Language: {request.language}, Text length: {len(request.text)}")
        
        # Generate audio with language support (Google TTS returns MP3, pyttsx3 returns WAV)
        audio_data = text_to_speech_stream(request.text, language=request.language, use_google_tts=True)
        
        # Determine media type based on audio format
        # OpenAI TTS returns MP3, Google TTS returns MP3, pyttsx3 returns WAV
        # Check first few bytes to determine format
        is_mp3 = audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb' or audio_data[:4] == b'\xff\xf3' or audio_data[:4] == b'\xff\xf2'
        media_type = "audio/mpeg" if is_mp3 else "audio/wav"
        file_ext = "mp3" if is_mp3 else "wav"
        
        # Return audio file
        return Response(
            content=audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{file_ext}"
            }
        )
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )
