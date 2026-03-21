"""
system_metrics.py — Gurukul Runtime Telemetry & Metrics Layer
=============================================================

Tracks runtime telemetry and exposes a /system/metrics JSON endpoint.

Tracked metrics:
  - API request count (total, per-route, per-status-code)
  - Error count and rate
  - Voice inference latency (rolling average)
  - AI / LLM inference latency (rolling average)
  - Process uptime
  - Watchdog status summary

Integration:
    In main.py include the metrics router:
        from app.services.system_metrics import metrics_router, MetricsMiddleware
        app.add_middleware(MetricsMiddleware)
        app.include_router(metrics_router)
"""

import time
import threading
import logging
from collections import defaultdict, deque
from typing import Dict, Deque

from fastapi import APIRouter, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("SystemMetrics")

# ---------------------------------------------------------------------------
# Internal state — module-level, thread-safe via a lock
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_start_time: float = time.time()

# Request counters
_total_requests: int = 0
_error_count: int = 0          # HTTP 5xx responses
_status_counts: Dict[int, int] = defaultdict(int)   # {status_code: count}
_route_counts: Dict[str, int] = defaultdict(int)    # {route: count}

# Latency rolling windows (last 500 samples each)
_WINDOW = 500
_voice_latencies: Deque[float] = deque(maxlen=_WINDOW)
_ai_latencies: Deque[float] = deque(maxlen=_WINDOW)


# ---------------------------------------------------------------------------
# Public API for recording events from other services
# ---------------------------------------------------------------------------

def record_voice_latency(latency_ms: float):
    """Call from voice_provider.py after each synthesis."""
    with _lock:
        _voice_latencies.append(latency_ms)


def record_ai_latency(latency_ms: float):
    """Call from llm.py / sovereign_lm_core.py after each inference."""
    with _lock:
        _ai_latencies.append(latency_ms)


def _avg(dq: Deque[float]) -> float:
    return round(sum(dq) / len(dq), 2) if dq else 0.0


def _p95(dq: Deque[float]) -> float:
    if not dq:
        return 0.0
    sorted_vals = sorted(dq)
    idx = int(len(sorted_vals) * 0.95)
    return round(sorted_vals[min(idx, len(sorted_vals) - 1)], 2)


# ---------------------------------------------------------------------------
# FastAPI middleware — counts requests & latencies automatically
# ---------------------------------------------------------------------------

class MetricsMiddleware(BaseHTTPMiddleware):
    """Transparent request-counting and response-time middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        global _total_requests, _error_count

        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        route = request.url.path
        status = response.status_code

        with _lock:
            _total_requests += 1
            _status_counts[status] += 1
            _route_counts[route] += 1
            if status >= 500:
                _error_count += 1

        return response


# ---------------------------------------------------------------------------
# /system/metrics endpoint
# ---------------------------------------------------------------------------

metrics_router = APIRouter(prefix="/system", tags=["Infrastructure"])


@metrics_router.get("/metrics")
async def get_metrics():
    """
    Telemetry snapshot for the Gurukul runtime.

    Returns:
        - uptime
        - request counts by status code and route
        - error rate
        - voice and AI latency stats
        - watchdog status (if started)
    """
    with _lock:
        total = _total_requests
        errors = _error_count
        status_snapshot = dict(_status_counts)
        route_snapshot = dict(sorted(_route_counts.items(), key=lambda x: -x[1])[:20])
        voice_avg = _avg(_voice_latencies)
        voice_p95 = _p95(_voice_latencies)
        voice_samples = len(_voice_latencies)
        ai_avg = _avg(_ai_latencies)
        ai_p95 = _p95(_ai_latencies)
        ai_samples = len(_ai_latencies)

    uptime_s = time.time() - _start_time
    error_rate = round((errors / total * 100), 2) if total > 0 else 0.0

    # Pull watchdog status non-blocking
    watchdog_status = {}
    try:
        from app.services.service_watchdog import watchdog
        watchdog_status = watchdog.get_status()
    except Exception as exc:
        watchdog_status = {"error": f"Could not read watchdog: {exc}"}

    return {
        "uptime_seconds": round(uptime_s, 1),
        "uptime_human": _format_uptime(uptime_s),
        "requests": {
            "total": total,
            "error_count": errors,
            "error_rate_percent": error_rate,
            "by_status_code": status_snapshot,
            "top_routes": route_snapshot,
        },
        "latency": {
            "voice_inference": {
                "avg_ms": voice_avg,
                "p95_ms": voice_p95,
                "samples": voice_samples,
            },
            "ai_inference": {
                "avg_ms": ai_avg,
                "p95_ms": ai_p95,
                "samples": ai_samples,
            },
        },
        "watchdog": watchdog_status,
    }


@metrics_router.post("/metrics/reset")
async def reset_metrics():
    """Reset all runtime counters (useful after maintenance windows)."""
    global _total_requests, _error_count, _start_time
    with _lock:
        _total_requests = 0
        _error_count = 0
        _status_counts.clear()
        _route_counts.clear()
        _voice_latencies.clear()
        _ai_latencies.clear()
        _start_time = time.time()
    return {"message": "Metrics reset successfully", "timestamp": time.time()}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_uptime(seconds: float) -> str:
    d = int(seconds // 86400)
    h = int((seconds % 86400) // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)
