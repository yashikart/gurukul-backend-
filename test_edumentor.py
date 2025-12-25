"""
Test script for EduMentor endpoint
"""
import requests
import json

# Test the endpoint with valid JSON
url = "http://localhost:3000/agent/edumentor/generate"

# Valid JSON request (using lowercase true/false)
payload = {
    "subject": "Physics",
    "topic": "Newton's Laws",
    "include_wikipedia": True,  # This will be converted to true in JSON
    "use_knowledge_store": False,
    "use_orchestration": False,
    "provider": "auto"
}

print("Testing EduMentor endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*50 + "\n")

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

