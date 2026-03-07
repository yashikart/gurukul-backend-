from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import os
import voice_engine_interface as vaani

app = FastAPI(title="Vaani Sentinel: Voice Service API")

class VoiceRequest(BaseModel):
    text: str
    language: str = "en"
    voice_profile: str = "vaani_teacher"

@app.get("/health")
async def health():
    engine = vaani.get_engine()
    return {
        "status": "healthy" if engine.model else "initializing",
        "device": engine.device
    }

@app.post("/voice/speak")
async def speak(request: VoiceRequest):
    """
    Standardized API endpoint for sovereign voice generation.
    """
    # Use the standardized interface
    output_path, error = vaani.generate_voice(
        text=request.text,
        language=request.language,
        voice_profile=request.voice_profile
    )

    if error:
        # Handle empty string or inference errors as identified in audit
        status_code = 422 if "Empty" in error else 500
        raise HTTPException(status_code=status_code, detail=error)

    # Read audio data
    try:
        with open(output_path, "rb") as f:
            audio_data = f.read()
            
        # Optional: Clean up temporary file after reading if needed, 
        # but for performance we might keep them in a cache dir.
        # os.remove(output_path) 

        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(output_path)}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File read error: {e}")

if __name__ == "__main__":
    import uvicorn
    # Running on 8008 to maintain compatibility with Task 1 backend proxy
    uvicorn.run(app, host="0.0.0.0", port=8008)
