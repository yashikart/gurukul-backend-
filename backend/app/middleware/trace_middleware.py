from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import set_trace_id
import logging

logger = logging.getLogger("TraceMiddleware")

async def trace_id_middleware(request: Request, call_next):
    """
    Middleware to extract trace_id from headers and set it in context.
    Follows TANTRA integration rules:
    - Accept x-trace-id from headers.
    - If missing, set to None (null).
    - DO NOT generate a new trace_id.
    """
    trace_id = request.headers.get("x-trace-id")
    
    # Set in context
    set_trace_id(trace_id)
    
    # Optional: Tag the request for internal logging if trace_id exists
    if trace_id:
        logger.debug(f"Request assigned trace_id: {trace_id}")
    
    response = await call_next(request)
    
    # Propagate back to response headers for visibility
    if trace_id:
        response.headers["x-trace-id"] = trace_id
        
    return response
