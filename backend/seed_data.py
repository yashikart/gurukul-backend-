
# Seed Data Script for Gurukul
import sys
import os
import bcrypt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.all_models import Tenant, User, Profile

# Basic bcrypt helper for seeding script only
def get_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

sys.path.append(os.getcwd())

def seed_db():
    print("--- Seeding Database Start ---")
    db = SessionLocal()
    print(f"DEBUG: Using DB URL: {db.bind.url}")
    
    try:
        # 1. Tenant
        tenant = db.query(Tenant).filter(Tenant.name == "Gurukul Main").first()
        if not tenant:
            tenant = Tenant(name="Gurukul Main", type="INSTITUTION")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"Created Tenant: {tenant.id}")
        else:
            print(f"Tenant Exists: {tenant.id}")

        # 2. Users
        password_hash = get_hash("password123")
        
        users_to_create = [
            {"email": "admin@gurukul.com", "role": "ADMIN", "name": "Admin User"},
            {"email": "teacher@gurukul.com", "role": "TEACHER", "name": "Guru Dronacharya"},
            {"email": "parent@gurukul.com", "role": "PARENT", "name": "Parent User"},
            {"email": "student@gurukul.com", "role": "STUDENT", "name": "Arjuna Student"}
        ]
        
        for u in users_to_create:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                new_user = User(
                    email=u["email"],
                    hashed_password=password_hash,
                    full_name=u["name"],
                    role=u["role"], # Uppercase match
                    tenant_id=tenant.id
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                # Profile
                db.add(Profile(user_id=new_user.id, data={}))
                db.commit()
                print(f"Created User: {u['email']}")
            else:
                # Update password just in case it was wrong
                existing.hashed_password = password_hash
                existing.role = u["role"] # fix case if needed
                db.commit()
                print(f"Updated User: {u['email']}")

    except Exception as e:
        print(f"SEED ERROR: {e}")
        db.rollback()
    finally:
        db.close()
        print("--- Seeding Database End ---")

if __name__ == "__main__":
    seed_db()
