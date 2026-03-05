# Demo Tenant Seeding Script for Gurukul
import sys
import os
import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.all_models import Tenant, User, Profile, Cohort, TeacherStudentAssignment, SubjectData

def get_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_demo_env():
    print("--- Seeding Demo Environment Start ---")
    db = SessionLocal()
    
    try:
        # 1. Create Demo Tenant
        tenant_name = "demo.gurukul.blackholeinfiverse.com"
        demo_tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
        if not demo_tenant:
            demo_tenant = Tenant(name=tenant_name, type="INSTITUTION")
            db.add(demo_tenant)
            db.commit()
            db.refresh(demo_tenant)
            print(f"Created Demo Tenant: {demo_tenant.id}")
        else:
            print(f"Demo Tenant already exists: {demo_tenant.id}")

        # 2. Create Demo Cohort
        demo_cohort = db.query(Cohort).filter(Cohort.name == "Demo Class 10-A", Cohort.tenant_id == demo_tenant.id).first()
        if not demo_cohort:
            demo_cohort = Cohort(name="Demo Class 10-A", tenant_id=demo_tenant.id)
            db.add(demo_cohort)
            db.commit()
            db.refresh(demo_cohort)
            print("Created Demo Cohort")

        # 3. Create Users
        password_hash = get_hash("demo123")
        
        users_to_create = [
            {"email": "admin@demo.com", "role": "ADMIN", "name": "Demo Admin", "cohort_id": None},
            {"email": "teacher@demo.com", "role": "TEACHER", "name": "Demo Teacher", "cohort_id": None},
            {"email": "parent@demo.com", "role": "PARENT", "name": "Demo Parent", "cohort_id": None},
            {"email": "student@demo.com", "role": "STUDENT", "name": "Demo Student", "cohort_id": demo_cohort.id}
        ]
        
        created_users = {}
        
        for u in users_to_create:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                new_user = User(
                    email=u["email"],
                    hashed_password=password_hash,
                    full_name=u["name"],
                    role=u["role"],
                    tenant_id=demo_tenant.id,
                    cohort_id=u["cohort_id"]
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                created_users[u["role"]] = new_user
                
                # Profile with some realistic data
                profile_data = {}
                if u["role"] == "STUDENT":
                    profile_data = {"grade": "10", "learning_style": "Visual"}
                elif u["role"] == "TEACHER":
                    profile_data = {"subjects_taught": ["Science", "Math"]}
                    
                db.add(Profile(user_id=new_user.id, data=profile_data))
                db.commit()
                print(f"Created User: {u['email']}")
            else:
                existing.hashed_password = password_hash
                existing.tenant_id = demo_tenant.id
                existing.cohort_id = u["cohort_id"]
                db.commit()
                created_users[u["role"]] = existing
                print(f"Updated User: {u['email']}")
                
        # Link Parent and Student
        if "PARENT" in created_users and "STUDENT" in created_users:
            student = created_users["STUDENT"]
            student.parent_id = created_users["PARENT"].id
            db.commit()
            print("Linked Student to Parent")

        # Teacher Student Assignment
        if "TEACHER" in created_users and "STUDENT" in created_users:
            assignment = db.query(TeacherStudentAssignment).filter(
                TeacherStudentAssignment.teacher_id == created_users["TEACHER"].id,
                TeacherStudentAssignment.student_id == created_users["STUDENT"].id
            ).first()
            
            if not assignment:
                assignment = TeacherStudentAssignment(
                    teacher_id=created_users["TEACHER"].id,
                    student_id=created_users["STUDENT"].id,
                    cohort_id=demo_cohort.id,
                    subject="Science"
                )
                db.add(assignment)
                db.commit()
                print("Assigned Teacher to Student")

        # Populate some realistic demo data (SubjectData)
        if "STUDENT" in created_users:
            student_id = created_users["STUDENT"].id
            existing_data = db.query(SubjectData).filter(SubjectData.user_id == student_id).first()
            if not existing_data:
                demo_subject = SubjectData(
                    user_id=student_id,
                    subject="Science",
                    topic="Photosynthesis",
                    notes="Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water."
                )
                db.add(demo_subject)
                db.commit()
                print("Added realistic demo SubjectData")

        print("--- Demo Environment Setup Complete ---")
        
    except Exception as e:
        print(f"DEMO SEED ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_env()
