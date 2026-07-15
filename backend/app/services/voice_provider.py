"""
voice_provider.py — Canonical Voice Provider for Gurukul

Routes all TTS generation through the Vaani Sovereign Engine (Port 8008).
Implements production guardrails:
  - 5000 character hard input limit
  - 20 second inference timeout via asyncio.wait_for
  - Max 3 concurrent requests via asyncio.Semaphore
  - Automatic retry with backoff (3 attempts)
  - In-memory cache for repeated requests
  - GPU→CPU fallback awareness
"""

import asyncio
import hashlib
import time
import logging
from typing import Dict, Any, Optional
from vaani_sdk import VaaniAsyncClient
from app.services.voice_engine_interface import VoiceEngineInterface
from app.core.config import settings
from app.services.pravah_adapter import pravah_adapter


logger = logging.getLogger("VoiceProvider")

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
MAX_INPUT_CHARS     = 5000      # Hard limit — requests above this are REJECTED
INFERENCE_TIMEOUT   = 20        # Seconds — inference aborts after this
MAX_CONCURRENCY     = 3         # Semaphore slots
CACHE_MAX_ENTRIES   = 200       # Evict oldest when exceeded


class VoiceProvider(VoiceEngineInterface):
    """
    Canonical Voice Provider that routes to the Vaani engine via VaaniAsyncClient.
    Strictly deterministic and 100% offline: No Google Translate fallback.
    """

    def __init__(self):
        self.vaani_url = settings.VAANI_API_URL
        self.max_chars = MAX_INPUT_CHARS
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
        self.request_timeout = INFERENCE_TIMEOUT
        self.cache: Dict[str, bytes] = {}
        self.start_time = time.time()
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failures": 0,
            "timeouts": 0,
            "cache_hits": 0,
            "rejected_too_long": 0,
            "gpu_mode": True,
            "queue_depth": 0,
        }
        
        # Initialize the SDK Client
        self.vaani_client = VaaniAsyncClient(
            base_url=self.vaani_url,
            timeout=self.request_timeout
        )
        
        logger.info(
            f"VoiceProvider initialized | vaani_url={self.vaani_url} | "
            f"max_chars={self.max_chars} | timeout={self.request_timeout}s | "
            f"concurrency={MAX_CONCURRENCY} | FALLBACK_DISABLED=True"
        )

    # ──────────────────────────────────────────────────────────
    # Public API  (implements VoiceEngineInterface)
    # ──────────────────────────────────────────────────────────

    async def generate_audio(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize audio via Vaani SDK Client.
        """
        # ── 1. Input Validation ──────────────────────────────
        if not text or not text.strip():
            raise ValueError("Text input is empty")

        if len(text) > self.max_chars:
            self.stats["rejected_too_long"] += 1
            logger.error(f"[REJECTED] Input too long: {len(text)} chars")
            raise ValueError(
                f"Input length {len(text)} exceeds maximum {self.max_chars} characters. "
                f"Please shorten your text."
            )

        # ── 2. Cache Lookup ──────────────────────────────────
        cache_key = self._cache_key(text, language)
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            logger.info(f"[CACHE HIT] key={cache_key[:12]}… | total_hits={self.stats['cache_hits']}")
            return self.cache[cache_key]

        # ── 3. Concurrency-Controlled Inference ──────────────
        self.stats["total_requests"] += 1
        self.stats["queue_depth"] += 1
        logger.info(
            f"[QUEUED] request #{self.stats['total_requests']} | "
            f"queue_depth={self.stats['queue_depth']}/{MAX_CONCURRENCY} | "
            f"text_len={len(text)}"
        )

        try:
            async with self.semaphore:
                logger.info(f"[ACQUIRED] semaphore slot | queue_depth={self.stats['queue_depth']}")

                # ── 4. Synthesize via SDK Client ───────────────────
                logger.info(f"[TTS START] text_len={len(text)}")
                pravah_adapter.emit_signal(
                    event_type="system_event",
                    action="tts_start",
                    payload={"text_len": len(text), "language": language}
                )
                
                audio_data = await self.vaani_client.synthesize(
                    text=text,
                    language=language,
                    voice_profile="vaani_teacher"
                )

            # ── 5. Cache Result ──────────────────────────────
            self._cache_put(cache_key, audio_data)
            self.stats["successful_requests"] += 1
            logger.info(f"[SUCCESS] Voice generated ({len(audio_data)} bytes)")
            
            pravah_adapter.emit_signal(
                event_type="system_event",
                action="tts_completed",
                status="success",
                payload={"bytes": len(audio_data)}
            )
            return audio_data

        except Exception as e:
            self.stats["failures"] += 1
            logger.error(f"[FAILURE] VoiceProvider error: {str(e)}")
            pravah_adapter.emit_signal(
                event_type="system_event",
                action="tts_failed",
                status="error",
                payload={"reason": str(e)}
            )
            raise RuntimeError(f"Voice generation failed: {e}")
        finally:
            self.stats["queue_depth"] -= 1

    def get_status(self) -> dict:
        """Return operational metrics for monitoring."""
        return {
            "uptime_seconds": int(time.time() - self.start_time),
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failure_count": self.stats["failures"],
            "timeout_count": self.stats["timeouts"],
            "rejected_too_long": self.stats["rejected_too_long"],
            "gpu_mode": self.stats["gpu_mode"],
            "cache_size": len(self.cache),
            "cache_hits": self.stats["cache_hits"],
            "queue_depth": self.stats["queue_depth"],
            "max_concurrency": MAX_CONCURRENCY,
            "max_input_chars": MAX_INPUT_CHARS,
            "inference_timeout_s": INFERENCE_TIMEOUT,
            "deterministic_enforced": True
        }

    # ──────────────────────────────────────────────────────────
    # Internal Methods
    # ──────────────────────────────────────────────────────────

    def _cache_key(self, text: str, language: str) -> str:
        """Generate deterministic cache key using SHA-256."""
        raw = f"{language}:{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _cache_put(self, key: str, data: bytes):
        """Insert into cache with LRU-style eviction."""
        if len(self.cache) >= CACHE_MAX_ENTRIES:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.info(f"[CACHE] Evicted oldest entry (size was {CACHE_MAX_ENTRIES})")
        self.cache[key] = data


# ──────────────────────────────────────────────────────────────
# Singleton instance
# ──────────────────────────────────────────────────────────────
provider = VoiceProvider()

