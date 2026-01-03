
import sys
import os
import bcrypt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.all_models import User, Tenant, Profile

sys.path.append(os.getcwd())

def upsert_admin(email, password_text):
    print(f"--- Configuring Admin: {email} ---")
    db = SessionLocal()
    try:
        # Ensure Tenant Exists
        tenant = db.query(Tenant).filter(Tenant.name == "Gurukul Main").first()
        if not tenant:
            print("Creating default tenant...")
            tenant = Tenant(name="Gurukul Main", type="INSTITUTION")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        user = db.query(User).filter(User.email == email).first()
        
        # Hash password for local DB (even if Supabase handles auth, we keep it consistent)
        hashed_pw = bcrypt.hashpw(password_text.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if user:
            print(f"User exists. Updating role to ADMIN.")
            user.role = "ADMIN"
            user.hashed_password = hashed_pw # Update local hash just in case
            user.tenant_id = tenant.id
        else:
            print(f"User not found locally. Creating new ADMIN record.")
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
        
        # Ensure profile
        if not db.query(Profile).filter(Profile.user_id == user.id).first():
            db.add(Profile(user_id=user.id, data={}))
            db.commit()
            
        print(f"SUCCESS: {email} is now configured as ADMIN in the backend.")
        print("IMPORTANT: You must still 'Sign Up' or ensure this user exists in Supabase/Auth provider.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    upsert_admin("blackholeinfiverse48@gmail.com", "admin123")
