import os
import hashlib
import requests
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class VaaniClient:
    def __init__(self, base_url: str = settings.VAANI_API_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def generate_hash(self, text: str, language: str) -> str:
        """Generate SHA256 hash for caching."""
        payload = f"{text}|{language}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    async def login(self):
        """
        Placeholder for auth flow if needed. 
        Currently Vaani Sentinel internal service doesn't require separate auth on localhost:8008.
        """
        return {"status": "success", "message": "Authenticated with Vaani Sentinel"}

    async def generate_tts(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Calls Vaani Sentinel to generate audio.
        Returns metadata including audio_id (hash) and status.
        """
        text_hash = self.generate_hash(text, language)
        
        try:
            # Check cache logic would go here (implemented in calling router or database helper)
            
            payload = {
                "text": text,
                "language": language,
                "voice_profile": "vaani_teacher"
            }
            
            # Using /voice/speak from voice_service_api.py
            response = self.session.post(
                f"{self.base_url}/voice/speak",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                # In a real system, we'd save this to a persistent storage/bucket
                # For now, we return the audio data or a reference
                return {
                    "status": "success",
                    "audio_id": text_hash,
                    "audio_data": response.content,
                    "media_type": "audio/wav"
                }
            else:
                logger.error(f"Vaani API error: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"Vaani service error: {response.status_code}"}
                
        except Exception as e:
            logger.exception("Vaani generation failed")
            return {"status": "error", "message": str(e)}

    async def download_audio(self, audio_id: str):
        """
        Retrieve audio from cache/storage.
        """
        # Logic to fetch from MongoDB/FS based on audio_id
        pass

vaani_client = VaaniClient()
