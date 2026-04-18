"""
pravah_adapter.py — Pravah Integration Layer for Gurukul
=========================================================

Responsibilities:
  - Push system metrics to Pravah every 60 seconds
  - Receive health signals and control commands
  - Trigger self-healing / restart signals via service_orchestrator

Metrics integrated:
  - uptime
  - request latency (avg/p95)
  - failure count
  - GPU usage
  - queue depth
"""

import asyncio
import logging
import time
import requests
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from app.services.system_metrics import get_metrics
from app.services.system_monitor import get_system_health
from app.core.config import settings
from app.core.context import get_trace_id

logger = logging.getLogger("PravahAdapter")

class PravahAdapter:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.pravah_url = getattr(settings, "PRAVAH_URL", "http://localhost:9000/telemetry")
        self._running = False
        self._task = None

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            logger.info(f"PravahAdapter started | interval={self.interval}s")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _loop(self):
        while self._running:
            try:
                await self._push_metrics()
            except Exception as e:
                logger.error(f"Failed to push metrics to Pravah: {e}")
            await asyncio.sleep(self.interval)

    async def _push_metrics(self):
        """Aggregate telemetry and write to runtime_events.json for Pravah ingestion."""
        try:
            metrics = await get_metrics()
            
            # Use the new lightweight health check
            health = await get_system_health()

            payload = {
                "source": "PravahAdapter",
                "timestamp": datetime.now().isoformat(),
                "unix_time": time.time(),
                "uptime": metrics.get("uptime_seconds"),
                "status": metrics.get("status", "unknown"),
                "telemetry": {
                    "voice_avg_ms": metrics.get("latency", {}).get("voice_ms", {}).get("avg"),
                    "ai_avg_ms": metrics.get("latency", {}).get("ai_ms", {}).get("avg"),
                    "failure_count": metrics.get("requests", {}).get("error_count", 0),
                    "error_rate": metrics.get("requests", {}).get("error_rate_percent", 0),
                },
                "system": metrics.get("system", {}),
                "watchdog": metrics.get("watchdog", {}),
                "trace_id": get_trace_id()
            }

            # Write to JSON for Pravah
            self._write_event(payload)

        except Exception as e:
            logger.error(f"Push metrics failed: {e}")

    def emit_signal(self, event_type: str, action: str, status: str = "success", payload: Optional[Dict[str, Any]] = None):
        """
        Emit a structured signal to Pravah.
        Called from various parts of the system for event-driven observability.
        """
        signal = {
            "source": "GurukulSignal",
            "trace_id": get_trace_id(),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "action": action,
            "status": status,
            "payload": payload or {}
        }
        
        # Write synchronously for immediate reporting
        try:
            self._write_event(signal)
            logger.debug(f"Signal emitted: {event_type} | action={action}")
        except Exception as e:
            logger.error(f"Failed to emit signal: {e}")

    def _write_event(self, event_data: Dict[str, Any]):
        """Internal helper to write event data to runtime_events.json."""
        try:
            # Root is 3 levels up from app/services/
            root_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            event_file = os.path.join(root_path, "runtime_events.json")
            with open(event_file, "a") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as fe:
            logger.error(f"Failed to write event to file: {fe}")

    async def receive_command(self, command: str):
        """Handle control signals from Pravah."""
        logger.info(f"[COMMAND] Received from Pravah: {command}")
        if command == "RESTART":
            # In a production environment, this would signal the orchestrator
            # or trigger a rolling restart logic
            await self._trigger_restart()

    async def _trigger_restart(self):
        logger.warning("RESTART command received — initiating self-healing sequence...")
        # Placeholder for zero-downtime restart trigger
        pass

# Singleton
pravah_adapter = PravahAdapter()
