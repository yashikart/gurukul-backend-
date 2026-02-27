"""
API security layer: rate limiting, request validation, payload size limits.
"""
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

# In-memory rate limit (use Redis in production for multi-instance)
_rate_limit_store: dict[str, list[float]] = {}
_RATE_WINDOW = 60.0  # seconds
_MAX_REQUESTS_PER_WINDOW = 100
_MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MB


def _client_key(request: Request) -> str:
    """Key for rate limiting: IP + optional tenant."""
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host or "unknown")
    tenant = getattr(request.state, "tenant_context", None)
    tid = getattr(tenant, "tenant_id", None) or getattr(tenant, "tenant_slug", None) or ""
    return f"{ip}:{tid}"


def _trim_rate_window(key: str, now: float):
    """Keep only timestamps within RATE_WINDOW."""
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    times = _rate_limit_store[key]
    cutoff = now - _RATE_WINDOW
    _rate_limit_store[key] = [t for t in times if t > cutoff]


_PUBLIC_PATHS = {"/openapi.json", "/docs", "/redoc", "/", "/health"}


async def rate_limit_middleware(request: Request, call_next: Callable):
    """Reject if client exceeds MAX_REQUESTS_PER_WINDOW per RATE_WINDOW."""
    if request.url.path in _PUBLIC_PATHS:
        return await call_next(request)
    import time
    key = _client_key(request)
    now = time.time()
    _trim_rate_window(key, now)
    times = _rate_limit_store[key]
    if len(times) >= _MAX_REQUESTS_PER_WINDOW:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests"},
        )
    times.append(now)
    return await call_next(request)


async def payload_size_middleware(request: Request, call_next: Callable):
    """Reject request if Content-Length exceeds MAX_BODY_SIZE."""
    if request.url.path in _PUBLIC_PATHS:
        return await call_next(request)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > _MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": f"Payload too large (max {_MAX_BODY_SIZE // (1024*1024)} MB)"},
                )
        except ValueError:
            pass
    return await call_next(request)


def get_rate_limit_middleware():
    """Return the rate limit middleware for app.add_middleware."""
    return rate_limit_middleware


def get_payload_size_middleware():
    return payload_size_middleware
