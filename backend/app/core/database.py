
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    pool_pre_ping=True  # Verify connections before using (helps with PostgreSQL)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
