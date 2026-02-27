
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Request
from app.core.config import settings

# Determine DB URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Fallback: Use SQLite for local dev/testing if DATABASE_URL not set
# For production, set DATABASE_URL to PostgreSQL connection string
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./gurukul.db" # Fallback
    print("Warning: DATABASE_URL not set. Using SQLite fallback.")

# Create engine with SQLite-specific args only if using SQLite
connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,        # Permanent connections
    max_overflow=20,     # Burst capacity
    pool_timeout=30,     # Wait budget for connection
    pool_recycle=1800    # Refresh connections every 30m
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _single_db_session():
    """Single-tenant: yield one session from default engine."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db(request: Request = None):
    """
    Yield DB session. When MULTI_TENANT_ENABLED, uses request to resolve tenant and yields
    that tenant's DB session. Otherwise yields default DB.
    """
    import os
    # Re-read from env at runtime so changes take effect without restart
    multi_tenant = os.environ.get("MULTI_TENANT_ENABLED", "false").lower() == "true"
    if multi_tenant and request:
        from app.core.db_router import get_tenant_db
        for session in get_tenant_db(request):
            yield session
        return
    yield from _single_db_session()
