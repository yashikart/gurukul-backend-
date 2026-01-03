
import sys
import os
import bcrypt
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add CWD to path
sys.path.append(os.getcwd())

from app.models.all_models import User, Tenant, Profile, Base

# Force Absolute Path to DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gurukul.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"Connecting to: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def upsert_admin_robust(email, password_text):
    print(f"--- Promoting: {email} ---")
    
    # Check tables
    insp = inspect(engine)
    tables = insp.get_table_names()
    print(f"Existing Tables: {tables}")
    
    if "users" not in tables:
        print("CRITICAL: 'users' table missing. Creating tables...")
        Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Tenant
        tenant = db.query(Tenant).filter(Tenant.name == "Gurukul Main").first()
        if not tenant:
            tenant = Tenant(name="Gurukul Main", type="INSTITUTION")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        
        # User
        user = db.query(User).filter(User.email == email).first()
        hashed_pw = bcrypt.hashpw(password_text.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if user:
            print(f"User found. Current Role: {user.role}")
            user.role = "ADMIN"
            user.hashed_password = hashed_pw
            user.tenant_id = tenant.id
            db.commit()
            print("UPDATED: User is now ADMIN.")
        else:
            print("User not found locally. INSERTING new ADMIN.")
            user = User(
                email=email,
                hashed_password=hashed_pw,
                full_name="Admin User",
                role="ADMIN",
                tenant_id=tenant.id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Profile
            if not db.query(Profile).filter(Profile.user_id == user.id).first():
                db.add(Profile(user_id=user.id, data={}))
                db.commit()
            print("CREATED: User is now ADMIN.")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    upsert_admin_robust("blackholeinfiverse48@gmail.com", "admin123")
