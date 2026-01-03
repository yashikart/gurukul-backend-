
import sys
import os
import bcrypt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.all_models import User
from app.core.security import get_password_hash, verify_password

sys.path.append(os.getcwd())

def debug_users():
    print("--- Debugging Users ---")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users Found: {len(users)}")
        for u in users:
            print(f"User: {u.email} | Role: {u.role} | Hash Length: {len(u.hashed_password)}")
            
        print("\n--- Testing Hash ---")
        pw = "password123"
        print(f"Password: {pw}")
        try:
            h = get_password_hash(pw)
            print(f"Generated Hash: {h}")
            print(f"Verify: {verify_password(pw, h)}")
        except Exception as e:
            print(f"Hashing Failed: {e}")
            
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_users()
