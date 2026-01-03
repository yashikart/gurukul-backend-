
import sys
import os
import bcrypt
from app.core.database import SessionLocal
from app.models.all_models import User, Tenant, Profile

# Add CWD to path
sys.path.append(os.getcwd())

def promote_final(email, password_text):
    print(f"--- Promoting User: {email} ---")
    db = SessionLocal()
    print(f"DEBUG: Using DB URL: {db.bind.url}")
    
    try:
        # Check if users table exists by counting
        count = db.query(User).count()
        print(f"Total Users in DB: {count}")
        
        # 1. Ensure Tenant
        tenant = db.query(Tenant).filter(Tenant.name == "Gurukul Main").first()
        if not tenant:
            print("Creating Tenant...")
            tenant = Tenant(name="Gurukul Main", type="INSTITUTION")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        
        # 2. User
        user = db.query(User).filter(User.email == email).first()
        hashed_pw = bcrypt.hashpw(password_text.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if user:
            print(f"Found User. Current Role: {user.role}")
            user.role = "ADMIN"
            user.hashed_password = hashed_pw
            user.tenant_id = tenant.id
            db.commit()
            print("SUCCESS: User upgraded to ADMIN.")
        else:
            print("User not found. Creating new ADMIN...")
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
            print("SUCCESS: User created as ADMIN.")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    promote_final("blackholeinfiverse48@gmail.com", "admin123")
