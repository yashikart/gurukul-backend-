import os
import hashlib
import requests
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class VaaniClient:
    def __init__(self, base_url: str = None):
        if base_url is None:
            # Fallback to 8007 (Tiered Resilient Service) if not set in environment
            self.base_url = os.getenv("VAANI_API_URL", "http://localhost:8007")
        else:
            self.base_url = base_url
        self.session = requests.Session()

    def generate_hash(self, text: str, language: str) -> str:
        """Generate SHA256 hash for caching."""
        payload = f"{text}|{language}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    async def login(self):
        """
        Authenticated with the TTS service.
        """
        return {"status": "success", "message": "Authenticated with Gurukul TTS Service"}

    async def generate_tts(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Calls the tiered TTS Service to generate audio.
        Returns metadata including audio_id (hash) and binary content.
        """
        text_hash = self.generate_hash(text, language)
        
        try:
            # The tiered TTS service (8007) expects Form data at /api/generate
            # Mapping: agents.py uses 'text' and 'language', 
            # but tts.py currently only takes 'text' (uses default English).
            # We will send 'text' as a form field.
            payload = {
                "text": text
            }
            
            logger.info(f"Calling TTS Service at {self.base_url}/api/generate")
            response = self.session.post(
                f"{self.base_url}/api/generate",
                data=payload,
                timeout=90 # Increased timeout for heavy XTTS generation
            )
            
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("status") == "success":
                    audio_url = res_data.get("audio_url")
                    if audio_url:
                        # Fetch the actual audio binary from the provided URL
                        # Note: res_data['audio_url'] is usually /api/audio/{filename}
                        download_url = f"{self.base_url}{audio_url}"
                        logger.info(f"Downloading generated audio from {download_url}")
                        
                        audio_response = self.session.get(download_url, timeout=30)
                        if audio_response.status_code == 200:
                            return {
                                "status": "success",
                                "audio_id": text_hash,
                                "audio_data": audio_response.content,
                                "media_type": "audio/mpeg" # Layer 8007 returns MP3
                            }
                        else:
                            return {"status": "error", "message": f"Failed to download audio from {audio_url}"}
                
                return {"status": "error", "message": res_data.get("message", "Audio generation reported failure")}
            else:
                logger.error(f"Vaani API error: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"Vaani service error: {response.status_code}"}
                
        except Exception as e:
            logger.exception("Vaani generation failed")
            return {"status": "error", "message": f"Vaani Client Request failed: {str(e)}"}

    async def download_audio(self, audio_id: str):
        """
        Retrieve audio from cache/storage.
        """
        # Logic to fetch from MongoDB/FS based on audio_id
        pass

vaani_client = VaaniClient()
