
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Determine DB URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Fallback for now if no DB configured: Use SQLite for local dev/testing if preferred, 
# or just fail gracefully. For production hardening, we assume Postgres.
# If URL is None, we can't connect.
if not SQLALCHEMY_DATABASE_URL:
    # Construct from Supabase URL if possible? No, Supabase URL is HTTP.
    # We need the direct connection string.
    # print("Warning: DATABASE_URL not set. Database features will fail.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./gurukul.db" # Fallback

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
