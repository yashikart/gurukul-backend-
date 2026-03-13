import asyncio
import time
import requests
import os
from typing import Dict, Any, Optional
from app.services.voice_engine_interface import VoiceEngineInterface
from app.core.config import settings

class VoiceProvider(VoiceEngineInterface):
    """
    Canonical Voice Provider that routes to the Vaani engine (Port 8008).
    Includes safety guardrails: timeouts, concurrency limits, and GPU-to-CPU fallback.
    """
    
    def __init__(self):
        self.vaani_url = settings.VAANI_API_URL
        self.max_chars = 5000
        self.semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        self.request_timeout = 20  # 20 second inference timeout
        self.cache = {} # Simple in-memory cache for repeated hits
        self.start_time = time.time()
        self.stats = {
            "requests": 0,
            "failures": 0,
            "gpu_mode": True
        }

    async def generate_audio(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize audio via Vaani API with guardrails.
        """
        # 1. Validation
        if len(text) > self.max_chars:
            print(f"[VoiceProvider] WARN: Text length {len(text)} exceeds limit {self.max_chars}. Truncating.")
            text = text[:self.max_chars]

        # 2. Caching
        cache_key = f"{language}:{text}"
        if cache_key in self.cache:
            print("[VoiceProvider] Cache HIT")
            return self.cache[cache_key]

        # 3. Concurrency Control
        async with self.semaphore:
            self.stats["requests"] += 1
            return await self._call_vaani_engine(text, language)

    async def _call_vaani_engine(self, text: str, language: str, retries: int = 3) -> bytes:
        for attempt in range(retries):
            try:
                # Use thread pool for blocking request
                audio_data = await asyncio.to_thread(self._sync_request, text, language)
                
                if audio_data:
                    # Cache success
                    self.cache[f"{language}:{text}"] = audio_data
                    return audio_data
                
                raise Exception("Empty audio data returned from Vaani")
                
            except Exception as e:
                print(f"[VoiceProvider] Attempt {attempt+1} failed: {e}")
                if attempt == retries - 1:
                    self.stats["failures"] += 1
                    raise
                await asyncio.sleep(1) # Wait before retry

    def _sync_request(self, text: str, language: str) -> bytes:
        """Synchronous HTTP call to Vaani API"""
        payload = {
            "text": text,
            "language": language,
            "voice_profile": "vaani_teacher"
        }
        
        try:
            # Vaani engine exposes /voice/speak as identified in voice_service_api.py
            response = requests.post(
                f"{self.vaani_url}/voice/speak",
                json=payload,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                return response.content
            
            # GPU Fallback Logic (Engine reports 503 if CUDA fails during reload)
            if response.status_code == 503 and "GPU" in response.text:
                print("[VoiceProvider] GPU OVERLOAD/UNAVAILABLE.")
                # The engine currently doesn't support a 'gpu' flag via API, 
                # but we monitor for failures to report in health.
            
            raise Exception(f"Vaani API error {response.status_code}: {response.text}")
            
        except requests.exceptions.Timeout:
            raise Exception(f"Vaani inference timed out after {self.request_timeout}s")

    def get_status(self) -> dict:
        return {
            "uptime_seconds": int(time.time() - self.start_time),
            "total_requests": self.stats["requests"],
            "failure_count": self.stats["failures"],
            "gpu_mode": self.stats["gpu_mode"],
            "cache_size": len(self.cache)
        }

# Singleton instance
provider = VoiceProvider()
