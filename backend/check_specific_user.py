
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.all_models import User

# Force Abs Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gurukul.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def list_users():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"--- Users in {DB_PATH} ---")
    for u in users:
        print(f"ID: {u.id} | Email: '{u.email}' | Role: '{u.role}'")
    db.close()

if __name__ == "__main__":
    list_users()
