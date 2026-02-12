
import sys
import os
from datetime import datetime
from pydantic import ValidationError

# Add app to path
sys.path.append(os.getcwd())

try:
    from app.schemas import StudentTestResultSync
    print("Successfully imported StudentTestResultSync")
except ImportError as e:
    print(f"Failed to import schemas: {e}")
    sys.exit(1)

def test_sync_schema():
    print("\nTesting StudentTestResultSync schema with list of questions...")
    
    test_data = {
        "student_email": "student@example.com",
        "school_id": 1,
        "gurukul_id": "test_123",
        "subject": "Math",
        "topic": "Algebra",
        "difficulty": "medium",
        "num_questions": 2,
        "questions": [
            {"id": 1, "text": "What is 1+1?", "options": ["1", "2", "3"], "answer": "2"},
            {"id": 2, "text": "What is 2+2?", "options": ["3", "4", "5"], "answer": "4"}
        ],
        "user_answers": {"1": "2", "2": "4"},
        "score": 2,
        "total_questions": 2,
        "percentage": 100.0,
        "synced_at": datetime.now().isoformat()
    }
    
    try:
        sync_obj = StudentTestResultSync(**test_data)
        print("✅ SUCCESS: StudentTestResultSync accepted list of questions!")
        print(f"Questions type: {type(sync_obj.questions)}")
    except ValidationError as e:
        print("❌ FAILED: StudentTestResultSync rejected list of questions")
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_sync_schema()
