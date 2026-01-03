
import sys
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.all_models import User

# Add backend directory to path
sys.path.append(os.getcwd())

def promote_to_admin(email):
    print(f"--- Promoting User: {email} ---")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Found User: {user.full_name} ({user.role})")
            user.role = "ADMIN"
            db.commit()
            print(f"SUCCESS: User {email} is now an ADMIN.")
        else:
            print(f"ERROR: User {email} not found in local database.")
            print("Ensure you have signed up AND logged in at least once so the backend captures your user.")
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_email = sys.argv[1]
        promote_to_admin(target_email)
    else:
        print("Usage: python promote_user.py <email>")
