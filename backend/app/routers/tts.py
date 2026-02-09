from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import pyttsx3
import io
import tempfile
import os

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

@router.post("/vaani")
async def vaani_text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Vaani TTS (pyttsx3 - offline)
    Fast, offline text-to-speech using system voices
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long (max 10000 characters)")
        
        print(f"[Vaani TTS] Request received - Text length: {len(request.text)}")
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Configure TTS settings for better quality
        voices = engine.getProperty('voices')
        if voices:
            # Try to use a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate (words per minute)
        engine.setProperty('rate', 180)  # Slightly slower for clarity
        
        # Set volume (0.0 to 1.0)
        engine.setProperty('volume', 0.9)
        
        # Create temporary file for audio generation
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filepath = temp_file.name
        
        try:
            # Generate audio file
            engine.save_to_file(request.text, temp_filepath)
            engine.runAndWait()
            
            # Read the generated audio file
            if not os.path.exists(temp_filepath):
                raise HTTPException(status_code=500, detail="Audio generation failed - file not created")
            
            with open(temp_filepath, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Check if audio was generated
            if len(audio_data) == 0:
                raise HTTPException(status_code=500, detail="Audio generation failed - empty file")
            
            print(f"[Vaani TTS] Generated successfully ({len(audio_data)} bytes)")
            
            # Return audio file
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=vaani_speech.wav"
                }
            )
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except Exception as cleanup_error:
                    print(f"[Vaani TTS] Warning: Failed to cleanup temp file: {cleanup_error}")
    
    except Exception as e:
        print(f"[Vaani TTS] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech with Vaani TTS: {str(e)}"
        )
