from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, super_admin, schools, dashboard, teacher, student, parent, bucket
from app.routers.admin import dashboard as admin_dashboard
from app.config import settings

# Create database tables on startup
try:
    from app.models import StudentSummary, StudentFlashcard, StudentTestResult, StudentSubjectData
    Base.metadata.create_all(bind=engine)
    print("[Startup] Database tables created/verified successfully!")
except Exception as e:
    print(f"[Startup] Database table creation warning: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="School Management System API",
    description="Multi-tenant School Management System Backend",
    version="1.0.0"
)

# CORS middleware (configure for your frontend domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port (Gurukul frontend)
        "http://127.0.0.1:5173",
        "http://localhost:3001",  # EMS frontend port
        "http://127.0.0.1:3001",
        "https://ems-frontend-x7tr.onrender.com",  # EMS Frontend (Production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(super_admin.router)
app.include_router(schools.router)
app.include_router(dashboard.router)
app.include_router(admin_dashboard.router)  # School Admin Dashboard
app.include_router(teacher.router)  # Teacher Dashboard
app.include_router(student.router)  # Student Dashboard
app.include_router(parent.router)  # Parent Dashboard
app.include_router(bucket.router)  # BHIV Bucket PRANA ingest


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "School Management System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
