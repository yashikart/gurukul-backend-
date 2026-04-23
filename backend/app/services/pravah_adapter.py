"""
pravah_adapter.py — Real Pravah HTTP Connector for Gurukul (TANTRA Integration)
================================================================================

Responsibilities:
  - Emit structured signals to Pravah via real POST /pravah/ingest
  - Strict schema enforcement before transmission
  - Retry logic (max 3 attempts, 1s backoff)
  - Trace ID propagated on every signal
  - TANTRA_DEBUG_LOG=true → also writes to runtime_events.json (debug only)

Simulation Removed:
  - runtime_events.json is NO LONGER the source of truth
  - _write_event() removed; replaced with _http_emit()
"""

import asyncio
import logging
import time
import requests as http_client
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.services.tantra_schema_validator import validate_pravah_payload, ContractViolationError

logger = logging.getLogger("PravahAdapter")

_RETRY_MAX     = 3
_RETRY_BACKOFF = 1.0   # seconds between retries


class PravahAdapter:
    def __init__(self, interval: int = 60):
        from app.core.config import settings
        self.interval   = interval
        self.pravah_url = getattr(settings, "PRAVAH_URL", None)
        self.api_key    = getattr(settings, "TANTRA_API_KEY", None)
        self.debug_log  = getattr(settings, "TANTRA_DEBUG_LOG", False)
        self._running   = False
        self._task      = None

        if self.pravah_url:
            logger.info(f"PravahAdapter configured → {self.pravah_url}")
        else:
            logger.warning(
                "PravahAdapter: PRAVAH_URL not set — signals will be dropped (set env var to enable)"
            )

    # ── Lifecycle ───────────────────────────────────────────────────────────
    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            logger.info(f"PravahAdapter started | interval={self.interval}s")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    # ── Background loop ─────────────────────────────────────────────────────
    async def _loop(self):
        while self._running:
            try:
                await self._push_metrics()
            except Exception as e:
                logger.error(f"PravahAdapter loop error: {e}")
            await asyncio.sleep(self.interval)

    async def _push_metrics(self):
        """Aggregate system telemetry and push to Pravah."""
        from app.services.system_metrics import get_metrics
        from app.core.context import get_trace_id
        try:
            metrics = await get_metrics()
            payload = {
                "source":     "GurukulRuntime",
                "trace_id":   get_trace_id() or "system-loop",
                "timestamp":  datetime.now(timezone.utc).isoformat(),
                "event_type": "telemetry",
                "action":     "metrics_push",
                "status":     metrics.get("status", "unknown"),
                "payload": {
                    "uptime":         metrics.get("uptime_seconds"),
                    "total_requests": metrics.get("requests", {}).get("total", 0),
                    "error_count":    metrics.get("requests", {}).get("error_count", 0),
                    "error_rate":     metrics.get("requests", {}).get("error_rate_percent", 0),
                    "watchdog":       metrics.get("watchdog", {}),
                },
            }
            self._emit_signal_sync(payload)
        except Exception as e:
            logger.error(f"_push_metrics failed: {e}")

    # ── Public API ──────────────────────────────────────────────────────────
    def emit_signal(
        self,
        event_type: str,
        action: str,
        status: str = "success",
        payload: Optional[Dict[str, Any]] = None,
    ):
        """
        Emit a structured signal to Pravah.
        Validates schema, then sends via real HTTP POST with retry.
        Called from routers and services for event-driven observability.
        """
        from app.core.context import get_trace_id

        signal = {
            "source":     "GurukulRuntime",
            "trace_id":   get_trace_id() or "no-trace",
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "action":     action,
            "status":     status,
            "payload":    payload or {},
        }
        self._emit_signal_sync(signal)

    def _emit_signal_sync(self, signal: Dict[str, Any]) -> bool:
        """Validate + HTTP POST to Pravah, with retry. Synchronous (fire-and-forget safe)."""
        # 1. Schema validation — reject before sending
        try:
            validate_pravah_payload(signal)
        except ContractViolationError as e:
            logger.error(f"[Pravah] Payload rejected by schema validator: {e}")
            return False

        # 2. Debug log (optional — only if TANTRA_DEBUG_LOG=true)
        if self.debug_log:
            self._debug_write(signal)

        # 3. Real HTTP emission
        if not self.pravah_url:
            logger.debug("[Pravah] No URL configured — signal not sent (no-op).")
            return False

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-TANTRA-API-Key"] = self.api_key

        for attempt in range(1, _RETRY_MAX + 1):
            try:
                resp = http_client.post(
                    self.pravah_url,
                    json=signal,
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code in (200, 201, 202, 204):
                    logger.debug(
                        f"[Pravah] Signal sent ✓ | event={signal['event_type']} "
                        f"trace={signal['trace_id']} | attempt={attempt}"
                    )
                    return True
                else:
                    logger.warning(
                        f"[Pravah] Non-2xx response {resp.status_code} | attempt={attempt}/{_RETRY_MAX}"
                    )
            except Exception as e:
                logger.warning(f"[Pravah] HTTP error on attempt {attempt}/{_RETRY_MAX}: {e}")

            if attempt < _RETRY_MAX:
                time.sleep(_RETRY_BACKOFF)

        logger.error(
            f"[Pravah] All {_RETRY_MAX} attempts failed — signal dropped "
            f"(event={signal.get('event_type')} trace={signal.get('trace_id')})"
        )
        return False

    # ── Debug only (not source of truth) ────────────────────────────────────
    def _debug_write(self, event_data: Dict[str, Any]):
        """Write event to runtime_events.json for LOCAL DEBUG only. Not transmitted to TANTRA as source of truth."""
        try:
            root_path  = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            event_file = os.path.join(root_path, "runtime_events.json")
            with open(event_file, "a") as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as fe:
            logger.debug(f"[Pravah] Debug log write failed: {fe}")

    # ── Command receiver ─────────────────────────────────────────────────────
    async def receive_command(self, command: str):
        logger.info(f"[COMMAND] Received from Pravah: {command}")
        if command == "RESTART":
            await self._trigger_restart()

    async def _trigger_restart(self):
        logger.warning("RESTART command received — initiating self-healing sequence...")


# Singleton
pravah_adapter = PravahAdapter()
