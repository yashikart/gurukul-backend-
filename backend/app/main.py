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

# Initialize FastAPI IMMEDIATELY - this allows the server to start listening
# even if router imports are slow. We'll include routers after the app is created.
try:
    app = FastAPI(title=settings.API_TITLE)
    print(f"[Main] ✓ FastAPI app initialized with title: {settings.API_TITLE}")
    sys.stdout.flush()
except Exception as e:
    print(f"[Main] ✗ Error initializing FastAPI app: {e}")
    print(traceback.format_exc())
    sys.stdout.flush()
    sys.exit(1)

# DEFER router imports to startup event to allow server to start immediately
# This is critical - uvicorn waits for module to fully load before starting server
# By deferring router imports, we allow the server to start and bind to port first
print("[Main] Router imports will be deferred to startup event for faster server start")
sys.stdout.flush()

# Placeholder variables for routers - will be imported in startup event
chat = None
flashcards = None
learning = None
ems = None
summarizer = None
auth = None
soul = None
agents = None
quiz = None
journey = None
tts = None
ems_student = None
lesson = None
sovereign = None
vaani = None
bucket = None
ems_sync_manual = None

# Karma Tracker routers
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

# CORS - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (Gurukul Frontend)
        "http://localhost:3000",  # Alternative frontend port
        "http://localhost:3001",  # EMS frontend dev
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://gurukul-frontend-738j.onrender.com",  # Gurukul Frontend (Production)
        "https://ems-frontend-x7tr.onrender.com",  # EMS Frontend (Production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Startup
    import asyncio
    global chat, flashcards, learning, ems, summarizer, auth, soul, agents, quiz, journey, tts
    global ems_student, lesson, sovereign, vaani, bucket, ems_sync_manual
    global karma_router, balance, redeem, policy, feedback, analytics, agami, normalization
    global rnanubandhan, karma_v1_main, lifecycle, stats, log_action, appeal, atonement, death, event
    
    # Debug: Print port information
    port_from_env = os.getenv("PORT", "not set")
    print(f"\n{'='*50}")
    print(f"Gurukul API v2 (Refactored) Started at http://{settings.HOST}:{settings.PORT}")
    print(f"PORT from environment: {port_from_env}")
    print(f"PORT from settings: {settings.PORT}")
    print(f"Env: {os.getenv('ENV', 'dev')}")
    print(f"{'='*50}\n")
    sys.stdout.flush()
    
    # Import routers NOW (after server has started) - run in thread to avoid blocking
    def import_auth_router_sync():
        """Import and register auth router first (critical for registration/login)"""
        global auth
        try:
            print("[Startup] Importing auth router (critical path)...")
            sys.stdout.flush()
            from app.routers import auth as auth_mod
            auth = auth_mod
            
            # Register auth router immediately
            app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
            print("[Startup] ✓ Auth router registered at /api/v1/auth")
            
            # Verify routes are registered
            auth_routes = [route.path for route in app.routes if hasattr(route, 'path') and '/api/v1/auth' in route.path]
            print(f"[Startup] Registered auth routes: {len(auth_routes)} routes")
            if auth_routes:
                print(f"[Startup] Sample routes: {auth_routes[:3]}")
            sys.stdout.flush()
            return True
        except Exception as e:
            print(f"[Startup] ✗ CRITICAL: Failed to import auth router: {e}")
            print(traceback.format_exc())
            sys.stdout.flush()
            return False
    
    def import_other_routers_sync():
        """Import other routers (non-critical, can run in background)"""
        global chat, flashcards, learning, ems, summarizer, soul, agents, quiz, journey, tts
        global ems_student, lesson, sovereign, vaani, bucket, ems_sync_manual
        
        try:
            print("[Startup] Importing other routers (non-critical)...")
            sys.stdout.flush()
            from app.routers import chat as chat_mod, flashcards as flashcards_mod, learning as learning_mod
            from app.routers import ems as ems_mod
            # DISABLED: summarizer uses too much memory (LED model ~300MB)
            # from app.routers import summarizer as summarizer_mod
            summarizer_mod = None
            from app.routers import soul as soul_mod, agents as agents_mod, quiz as quiz_mod
            from app.routers import journey as journey_mod, tts as tts_mod, ems_student as ems_student_mod
            from app.routers import lesson as lesson_mod, sovereign as sovereign_mod, vaani as vaani_mod
            from app.routers import bucket as bucket_mod, ems_sync_manual as ems_sync_manual_mod
            
            # Assign to globals
            chat = chat_mod
            flashcards = flashcards_mod
            learning = learning_mod
            ems = ems_mod
            # DISABLED: summarizer uses too much memory
            # summarizer = summarizer_mod
            summarizer = None
            soul = soul_mod
            agents = agents_mod
            quiz = quiz_mod
            journey = journey_mod
            tts = tts_mod
            ems_student = ems_student_mod
            lesson = lesson_mod
            sovereign = sovereign_mod
            vaani = vaani_mod
            bucket = bucket_mod
            ems_sync_manual = ems_sync_manual_mod
            
            # Include routers
            app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
            app.include_router(flashcards.router, prefix="/api/v1/flashcards", tags=["Flashcards"])
            app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
            # DISABLED: summarizer uses too much memory
            # app.include_router(summarizer.router, prefix="/api/v1/ai", tags=["AI Utilities"])
            app.include_router(ems.router, prefix="/api/v1/ems", tags=["Admin (EMS)"])
            app.include_router(ems_student.router, tags=["EMS Student Integration"])
            app.include_router(ems_sync_manual.router, tags=["EMS Manual Sync"])
            app.include_router(soul.router, prefix="/api/v1/soul", tags=["Soul"])
            app.include_router(agents.router, prefix="/api/v1/agent", tags=["Agents"])
            app.include_router(quiz.router, prefix="/api/v1/quiz", tags=["Quiz"])
            app.include_router(journey.router, prefix="/api/v1/learning", tags=["Learning Journey"])
            app.include_router(tts.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])
            app.include_router(lesson.router, prefix="/api/v1/lesson", tags=["Lesson Context"])
            app.include_router(sovereign.router, prefix="/api/v1/sovereign", tags=["Sovereign Fusion Layer"])
            app.include_router(vaani.router, prefix="/api/v1/vaani", tags=["Vaani RL-TTS"])
            app.include_router(bucket.router, prefix="/api/v1", tags=["PRANA Bucket"])
            
            # Legacy shims
            # DISABLED: summarizer uses too much memory
            # app.include_router(summarizer.router, tags=["Legacy Summarizer"])
            app.include_router(flashcards.router, prefix="/flashcards", tags=["Legacy Flashcards"])
            app.include_router(soul.router, prefix="/api/v1/soul", tags=["Soul Alignment"])
            
            print("[Startup] ✓ Other routers imported and included")
            sys.stdout.flush()
        except Exception as e:
            print(f"[Startup] ⚠️  Error importing other routers: {e}")
            print(traceback.format_exc())
            sys.stdout.flush()
            # Continue to try loading Karma Tracker routers even if other routers fail
        
        # Import Karma Tracker routers
        try:
            print("[Startup] Importing Karma Tracker routers...")
            sys.stdout.flush()
            from app.routers.karma_tracker import karma as karma_router_mod
            from app.routers.karma_tracker import balance as balance_mod, redeem as redeem_mod
            from app.routers.karma_tracker import policy as policy_mod, feedback as feedback_mod
            from app.routers.karma_tracker import analytics as analytics_mod, agami as agami_mod
            from app.routers.karma_tracker import normalization as normalization_mod
            from app.routers.karma_tracker import rnanubandhan as rnanubandhan_mod
            from app.routers.karma_tracker.v1.karma import main as karma_v1_main_mod
            from app.routers.karma_tracker.v1.karma import lifecycle as lifecycle_mod
            from app.routers.karma_tracker.v1.karma import stats as stats_mod
            from app.routers.karma_tracker.v1.karma import log_action as log_action_mod
            from app.routers.karma_tracker.v1.karma import appeal as appeal_mod
            from app.routers.karma_tracker.v1.karma import atonement as atonement_mod
            from app.routers.karma_tracker.v1.karma import death as death_mod
            from app.routers.karma_tracker.v1.karma import event as event_mod
            
            # Assign to globals
            karma_router = karma_router_mod
            balance = balance_mod
            redeem = redeem_mod
            policy = policy_mod
            feedback = feedback_mod
            analytics = analytics_mod
            agami = agami_mod
            normalization = normalization_mod
            rnanubandhan = rnanubandhan_mod
            karma_v1_main = karma_v1_main_mod
            lifecycle = lifecycle_mod
            stats = stats_mod
            log_action = log_action_mod
            appeal = appeal_mod
            atonement = atonement_mod
            death = death_mod
            event = event_mod
            
            # Include routers
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
            
            print("[Startup] ✓ Karma Tracker routers imported and included")
            sys.stdout.flush()
        except Exception as e:
            print(f"[Startup] ⚠️  Error importing Karma Tracker routers: {e}")
            print(traceback.format_exc())
            sys.stdout.flush()
        
        return True  # Return success - individual router failures are logged but don't stop startup
    
    # CRITICAL: Import auth router first and wait for it (registration/login must work)
    # Other routers can load in background
    try:
        print("[Startup] Importing critical auth router...")
        sys.stdout.flush()
        # Wait for auth router with shorter timeout (should be fast)
        auth_success = await asyncio.wait_for(
            asyncio.to_thread(import_auth_router_sync),
            timeout=30.0  # 30 seconds should be enough for auth router
        )
        if auth_success:
            print("[Startup] ✓ Auth router registered. Registration/login endpoints are now available.")
            sys.stdout.flush()
        else:
            print("[Startup] ✗ CRITICAL: Auth router failed to load!")
            sys.stdout.flush()
    except asyncio.TimeoutError:
        print("[Startup] ✗ CRITICAL: Auth router import timeout after 30 seconds")
        print("[Startup] Registration/login will NOT work!")
        sys.stdout.flush()
    except Exception as e:
        print(f"[Startup] ✗ CRITICAL: Auth router import error: {e}")
        print(traceback.format_exc())
        sys.stdout.flush()
    
    # Import other routers in background (non-blocking)
    # These can take longer and don't block server startup
    async def import_other_routers_async():
        try:
            await asyncio.wait_for(
                asyncio.to_thread(import_other_routers_sync),
                timeout=120.0  # 2 minutes for other routers
            )
            print("[Startup] ✓ All other routers imported and registered.")
            sys.stdout.flush()
        except asyncio.TimeoutError:
            print("[Startup] ⚠️  Other routers import timeout after 2 minutes")
            print("[Startup] Some features may not be available.")
            sys.stdout.flush()
        except Exception as e:
            print(f"[Startup] ⚠️  Other routers import error: {e}")
            sys.stdout.flush()
    
    # Start importing other routers in background (don't wait)
    asyncio.create_task(import_other_routers_async())
    print("[Startup] Other routers are loading in background...")
    sys.stdout.flush()
    
    # Run blocking operations in background to avoid blocking server startup
    # These also run in background - don't wait for them
    async def init_database():
        try:
            from app.core.database import engine, Base
            from app.models import all_models
            from app.models import rl_models  # Import RL models to register them with Base
            print("[Startup] Creating database tables...")
            sys.stdout.flush()
            Base.metadata.create_all(bind=engine)
            print("[Startup] ✓ Database tables created successfully!")
            sys.stdout.flush()
        except Exception as e:
            print(f"[Startup] Database initialization failed: {e}")
            sys.stdout.flush()
    
    async def init_mongodb():
        try:
            from app.core.karma_database import get_db, get_client
            db = get_db()
            # Test connection with timeout
            print("[Startup] Testing MongoDB connection...")
            sys.stdout.flush()
            await asyncio.wait_for(
                asyncio.to_thread(db.command, 'ping'),
                timeout=5.0
            )
            print("[Startup] ✓ Karma Tracker MongoDB connected successfully!")
            sys.stdout.flush()
        except asyncio.TimeoutError:
            print("[Startup] ⚠️  Karma Tracker MongoDB connection timed out")
            print("[Startup]   Karma features may not work without MongoDB")
            sys.stdout.flush()
        except Exception as e:
            print(f"[Startup] ⚠️  Karma Tracker MongoDB connection failed: {e}")
            print("[Startup]   Karma features may not work without MongoDB")
            sys.stdout.flush()
    
    # DISABLED: Model loading uses too much memory (~300MB for LED model)
    # async def init_models():
    #     try:
    #         from download_models_on_startup import ensure_models_exist
    #         print("[Startup] Checking for model files...")
    #         sys.stdout.flush()
    #         await asyncio.to_thread(ensure_models_exist)
    #     except Exception as e:
    #         print(f"[Startup] Model download check skipped/failed: {e}")
    #         sys.stdout.flush()
    
    # Run all initialization tasks in background - don't wait for them
    # This allows startup event to return immediately so server can bind to port
    asyncio.create_task(init_database())
    asyncio.create_task(init_mongodb())
    # DISABLED: Model loading to save memory
    # asyncio.create_task(init_models())
    print("[Startup] ℹ️  Summarizer model loading DISABLED to save memory")
    
    
    print("[Startup] ✓ Startup event complete! Server will bind to port now.")
    print("[Startup] Background tasks (routers, DB, MongoDB, models) are running in background.")
    sys.stdout.flush()
    # Return immediately - don't wait for any background tasks

# Routers are imported and included in the startup event
# This allows the server to start immediately without waiting for router imports

# Root Health Check
@app.get("/")
async def root():
    return {"message": "Gurukul Backend API v2 is running", "docs": "/docs"}

# Health check endpoint for Render deployment
@app.get("/health")
async def health_check():
    """Simple health check endpoint that responds immediately"""
    return {"status": "healthy", "service": "Gurukul Backend API"}

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

# Legacy shims are included in the startup event along with other routers

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

# Final message to confirm module is fully loaded
print("[Main] ✓ Module fully loaded. App is ready for uvicorn to start server.")
print(f"[Main] App object: {app}")
sys.stdout.flush()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
