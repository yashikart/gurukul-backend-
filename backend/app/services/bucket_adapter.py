import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.context import get_trace_id
from app.core.config import settings

logger = logging.getLogger("BucketAdapter")

class BucketAdapter:
    """
    Adapter for emitting interaction memory events to TANTRA Bucket storage.
    Rules:
    - Gurukul MUST NOT store memory locally.
    - Only emit events.
    - Do not fail user requests if Bucket is unavailable.
    """
    def __init__(self):
        self.bucket_url = getattr(settings, "BUCKET_URL", None)
        self.enabled = self.bucket_url is not None

    def emit_memory(self, user_id: str, session_id: str, action: str, outcome: str, payload: Optional[Dict[str, Any]] = None):
        """
        Emit a structured memory event to Bucket.
        Schema: trace_id, user_id, session_id, action, outcome, timestamp
        """
        memory_event = {
            "trace_id": get_trace_id(),
            "user_id": user_id,
            "session_id": session_id,
            "action": action,
            "outcome": outcome,
            "payload": payload or {},
            "timestamp": datetime.now().isoformat(),
            "source": "GurukulRuntime"
        }
        
        # 1. Log locally for traceability
        logger.info(f"[BUCKET EMIT] action={action} | user={user_id} | trace={memory_event['trace_id']}")
        
        # 2. Emit to Bucket (simulated for now if URL missing)
        if not self.enabled:
            logger.debug("Bucket URL not configured, memory event emitted only to logs.")
            return

        try:
            # In a real integration, this would be an async HTTP call (but non-blocking/passive)
            # For now, we log the intended emission
            logger.debug(f"Sending memory to Bucket: {json.dumps(memory_event)}")
            # requests.post(self.bucket_url, json=memory_event, timeout=1.0)
        except Exception as e:
            logger.error(f"Failed to emit memory to Bucket: {e}")

# Singleton
bucket_adapter = BucketAdapter()
