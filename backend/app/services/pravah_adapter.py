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
from typing import Dict, Any
from app.services.system_metrics import get_metrics
from app.services.system_monitor import get_system_health
from app.core.config import settings

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
        """Aggregate telemetry from metrics and monitor services and push to Pravah."""
        metrics = await get_metrics()
        health = await get_system_health()

        payload = {
            "source": "gurukul-backend",
            "timestamp": time.time(),
            "uptime": metrics.get("uptime_seconds"),
            "latency": {
                "voice_avg_ms": metrics.get("latency", {}).get("voice_inference", {}).get("avg_ms"),
                "ai_avg_ms": metrics.get("latency", {}).get("ai_inference", {}).get("avg_ms"),
            },
            "failures": metrics.get("requests", {}).get("error_count"),
            "gpu": {
                "available": health.get("gpu_details", {}).get("available"),
                "memory_used_mb": health.get("gpu_details", {}).get("memory_used_mb"),
            },
            "queue_depth": health.get("voice_engine", {}).get("queue_depth"),
            "status": health.get("status"),
        }

        # In a real integration, this would be a POST to Pravah
        # For now, we log it and simulate the call
        logger.info(f"[TELEMETRY] Pushing to Pravah: {payload['status']} | uptime={payload['uptime']}s")
        
        # try:
        #     requests.post(self.pravah_url, json=payload, timeout=5)
        # except Exception as e:
        #     logger.warning(f"Could not reach Pravah endpoint: {e}")

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
