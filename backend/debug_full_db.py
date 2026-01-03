
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.all_models import User, Tenant

sys.path.append(os.getcwd())

# Use RELATIVE path to match app behavior
SQLALCHEMY_DATABASE_URL = "sqlite:///./gurukul.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def dump_db():
    db = SessionLocal()
    print(f"--- DB Dump (Relative Path) ---")
    
    try:
        # Check integrity
        print("Tables:")
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        for row in result:
            print(f" - {row[0]}")
            
        print("\n[Tenants]")
        tenants = db.query(Tenant).all()
        for t in tenants:
            print(f"ID: {t.id} | Name: {t.name}")

        print("\n[Users]")
        users = db.query(User).all()
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Role: {u.role} | TenantID: {u.tenant_id}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    db.close()

if __name__ == "__main__":
    dump_db()
