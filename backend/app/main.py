# Force output to stderr/stdout immediately
import sys
sys.stdout.flush()
sys.stderr.flush()

print("=" * 80, flush=True)
print("[Main] FILE LOADED - Starting Gurukul Backend...", flush=True)

import os
import uvicorn
import logging
import traceback

print(f"[Main] Python version: {sys.version}", flush=True)
print(f"[Main] Working directory: {os.getcwd()}", flush=True)
print(f"[Main] Python path: {sys.path[:3]}", flush=True)
sys.stdout.flush()

try:
    from fastapi import FastAPI, Request, status, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from app.core.config import settings
    print("[Main] ✓ FastAPI and core imports successful")
except Exception as e:
    print(f"[Main] ✗ Error importing FastAPI/core modules: {e}")
    print(traceback.format_exc())
    sys.exit(1)

logger = logging.getLogger(__name__)

# Import Routers with error handling
try:
    from app.routers import chat, flashcards, learning, ems, summarizer, auth, soul, agents, quiz, journey, tts, ems_student, lesson, sovereign, vaani, bucket
    from app.routers import ems_sync_manual
    print("[Import] ✓ Main routers imported successfully")
except Exception as e:
    print(f"[Import] ✗ Error importing main routers: {e}")
    print(traceback.format_exc())
    raise

# Import Karma Tracker routers (integrated) - Optional for now
karma_router = None
balance = None
redeem = None
policy = None
feedback = None
analytics = None
agami = None
normalization = None
rnanubandhan = None
karma_v1_main = None
lifecycle = None
stats = None
log_action = None
appeal = None
atonement = None
death = None
event = None

try:
    from app.routers.karma_tracker import karma as karma_router
    from app.routers.karma_tracker import balance, redeem, policy, feedback, analytics, agami, normalization, rnanubandhan
    from app.routers.karma_tracker.v1.karma import main as karma_v1_main, lifecycle, stats, log_action, appeal, atonement, death, event
    print("[Import] ✓ Karma Tracker routers imported successfully")
except Exception as e:
    print(f"[Import] ⚠️  Error importing Karma Tracker routers: {e}")
    print(traceback.format_exc())
    print("[Import] Continuing without Karma Tracker routers...")

# Initialize FastAPI
try:
    app = FastAPI(title=settings.API_TITLE)
    print(f"[Main] ✓ FastAPI app initialized with title: {settings.API_TITLE}")
except Exception as e:
    print(f"[Main] ✗ Error initializing FastAPI app: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# CORS - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://localhost:3001",  # EMS frontend
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"  # Allow all in development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print(f"\n{'='*50}")
    print(f"Gurukul API v2 (Refactored) Started at http://{settings.HOST}:{settings.PORT}")
    print(f"Env: {os.getenv('ENV', 'dev')}")
    print(f"{'='*50}\n")
    
    # Initialize database tables
    try:
        from app.core.database import engine, Base
        from app.models import all_models
        from app.models import rl_models  # Import RL models to register them with Base
        print("[Startup] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[Startup] ✓ Database tables created successfully!")
    except Exception as e:
        print(f"[Startup] Database initialization failed: {e}")
    
    # Initialize Karma Tracker MongoDB connection
    try:
        from app.core.karma_database import get_db, get_client
        db = get_db()
        # Test connection
        db.command('ping')
        print("[Startup] ✓ Karma Tracker MongoDB connected successfully!")
    except Exception as e:
        print(f"[Startup] ⚠️  Karma Tracker MongoDB connection failed: {e}")
        print("[Startup]   Karma features may not work without MongoDB")
    
    # Try to ensure models exist (Shim to keep original behavior)
    try:
        # Assuming download_models_on_startup.py is in the root (cwd)
        from download_models_on_startup import ensure_models_exist
        ensure_models_exist()
    except Exception as e:
        print(f"[Startup] Model download check skipped/failed: {e}")

# Include Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["Flashcards"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(summarizer.router, prefix="/api/v1/ai", tags=["AI Utilities"])
app.include_router(ems.router, prefix="/api/v1/ems", tags=["Admin (EMS)"])
app.include_router(ems_student.router, tags=["EMS Student Integration"])  # Router already has prefix
app.include_router(ems_sync_manual.router, tags=["EMS Manual Sync"])  # Router already has prefix
app.include_router(soul.router, prefix="/api/v1/soul", tags=["Soul"])
app.include_router(agents.router, prefix="/api/v1/agent", tags=["Agents"])
app.include_router(quiz.router, prefix="/api/v1/quiz", tags=["Quiz"])
app.include_router(journey.router, prefix="/api/v1/learning", tags=["Learning Journey"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])
app.include_router(lesson.router, prefix="/api/v1/lesson", tags=["Lesson Context"])
app.include_router(sovereign.router, prefix="/api/v1/sovereign", tags=["Sovereign Fusion Layer"])
app.include_router(vaani.router, prefix="/api/v1/vaani", tags=["Vaani RL-TTS"])
app.include_router(bucket.router, prefix="/api/v1", tags=["PRANA Bucket"])

# Karma Tracker routes (integrated) - Only include if imports succeeded
if karma_router is not None:
    try:
        app.include_router(karma_router.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(balance.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(redeem.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(policy.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(feedback.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Karma Analytics"])
        app.include_router(agami.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(normalization.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(rnanubandhan.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(karma_v1_main.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(lifecycle.router, prefix="/api/v1/karma/lifecycle", tags=["Karma Lifecycle"])
        app.include_router(stats.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(log_action.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(appeal.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(atonement.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(death.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        app.include_router(event.router, prefix="/api/v1/karma", tags=["Karma Tracker"])
        print("[Router] ✓ Karma Tracker routes included successfully")
    except Exception as e:
        print(f"[Router] ⚠️  Error including Karma Tracker routes: {e}")
        print(traceback.format_exc())
else:
    print("[Router] ⚠️  Karma Tracker routes not included (imports failed)")

# Root Health Check
@app.get("/")
async def root():
    return {"message": "Gurukul Backend API v2 is running", "docs": "/docs"}

# Legacy Shim for old endpoints if needed (optional)
# We might want to mount the old endpoints similarly or just rely on the new prefix.
# The user asked to "Refactor", implies we should probably match the old URLs if we want frontend to work immediately?
# The old main.py had "/summarize-pdf".
# My new router has "/api/v1/summarizer/summarize-pdf".
# IF I want to avoid breaking frontend, I should probably also include routers without prefix or redirect?
# For "Production Hardening", we should use versioned APIs.
# But "Do not break what already works".
# So I should probably alias the old routes or mount them at root as well?
# Let's add them at root for compatibility for now.

# Legacy Shims for Frontend Compatibility
app.include_router(summarizer.router, tags=["Legacy Summarizer"]) # Exposes /summarize-pdf
app.include_router(flashcards.router, prefix="/flashcards", tags=["Legacy Flashcards"]) # Exposes /flashcards/generate
app.include_router(soul.router, prefix="/api/v1/soul", tags=["Soul Alignment"]) # New Soul Router

# Global Exception Handler - Ensures CORS headers are included even on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that ensures CORS headers are included
    even when unhandled exceptions occur.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    # Return JSON response with CORS headers
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": type(exc).__name__
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with CORS headers.
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with CORS headers.
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
