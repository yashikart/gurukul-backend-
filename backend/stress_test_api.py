
import httpx
import asyncio
import time
import sys

BASE_URL = "https://gurukul-up9j.onrender.com/api/v1"
STUDENT_EMAIL = "student@gurukul.com"
PASSWORD = "password123"

async def stress_test_student_flow():
    print(f"--- Starting API Stress Test for {STUDENT_EMAIL} ---")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        print("\n[1/4] Testing Login...")
        start = time.time()
        try:
            login_resp = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": STUDENT_EMAIL, "password": PASSWORD}
            )
            login_resp.raise_for_status()
            token = login_resp.json().get("access_token")
            duration = time.time() - start
            print(f"✅ Login Success ({duration:.2f}s)")
        except Exception as e:
            print(f"❌ Login Failed: {e}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Fetch Subjects
        print("\n[2/4] Testing Fetch Subjects...")
        start = time.time()
        try:
            subjects_resp = await client.get(f"{BASE_URL}/subjects", headers=headers)
            subjects_resp.raise_for_status()
            subjects = subjects_resp.json()
            duration = time.time() - start
            print(f"✅ Fetch Subjects Success: Found {len(subjects)} subjects ({duration:.2f}s)")
        except Exception as e:
            print(f"❌ Fetch Subjects Failed: {e}")

        # 3. Fetch Lessons (Assuming there's a subject to pick)
        if subjects:
            # Picking the first subject to fetch lessons for
            # Note: The endpoint might be different depending on the actual implementation
            # Let's try /lessons/subject/{subject_id} or just /lessons
            print("\n[3/4] Testing Fetch Lessons...")
            start = time.time()
            try:
                lessons_resp = await client.get(f"{BASE_URL}/lessons", headers=headers)
                lessons_resp.raise_for_status()
                lessons = lessons_resp.json()
                duration = time.time() - start
                print(f"✅ Fetch Lessons Success: Found {len(lessons)} lessons ({duration:.2f}s)")
            except Exception as e:
                print(f"❌ Fetch Lessons Failed: {e}")
        else:
            print("\n[3/4] Skipping Fetch Lessons (No subjects found)")

        # 4. Chatbot Interaction
        print("\n[4/4] Testing Chatbot Interaction...")
        start = time.time()
        try:
            # Endpoint based on chat.py
            chat_payload = {
                "message": "Explain the concept of gravity in simple terms.",
                "context": "Basic Science",
                "chat_history": []
            }
            chat_resp = await client.post(
                f"{BASE_URL}/chat/message",
                json=chat_payload,
                headers=headers
            )
            chat_resp.raise_for_status()
            duration = time.time() - start
            print(f"✅ Chatbot Response Success ({duration:.2f}s)")
        except Exception as e:
            print(f"❌ Chatbot Interaction Failed: {e}")

    print("\n--- Stress Test Completed ---")

if __name__ == "__main__":
    asyncio.run(stress_test_student_flow())
