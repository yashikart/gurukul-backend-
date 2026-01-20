
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import Routers
from app.routers import chat, flashcards, learning, ems, summarizer, auth, soul, agents, quiz, journey, tts, ems_student, lesson
from app.routers import ems_sync_manual

# Initialize FastAPI
app = FastAPI(title=settings.API_TITLE)

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
        print("[Startup] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[Startup] ✓ Database tables created successfully!")
    except Exception as e:
        print(f"[Startup] Database initialization failed: {e}")
    
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
