import requests
import time
import uuid
import datetime
import builtins

log_file = open("test_api_log.txt", "w", encoding="utf-8")
def print(*args, **kwargs):
    kwargs['file'] = log_file
    builtins.print(*args, **kwargs)


BASE_URL = "http://localhost:3000/api/v1/bucket/prana"

def generate_payload(overrides=None):
    payload = {
        "user_id": str(uuid.uuid4()),
        "role": "student",
        "system_type": "gurukul",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cognitive_state": "ON_TASK",
        "active_seconds": 5.0,
        "idle_seconds": 0.0,
        "away_seconds": 0.0,
        "focus_score": 95.0,
        "raw_signals": {"mouse_clicks": 10, "keystrokes": 50}
    }
    if overrides:
        payload.update(overrides)
    return payload

def test_valid_submission():
    print("\n--- Testing Valid Submission ---")
    payload = generate_payload()
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code==200 else response.text}")
    assert response.status_code == 200, "Valid submission failed"
    data = response.json()
    assert "packet_id" in data
    assert data["status"] == "ingested"
    return data["packet_id"]

def test_invalid_payloads():
    print("\n--- Testing Invalid Payloads ---")
    payload = generate_payload()
    del payload["active_seconds"]
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Missing active_seconds Status: {response.status_code}")

    payload = generate_payload({"active_seconds": "five"})
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Wrong type Status: {response.status_code}")

def test_boundary_limits():
    print("\n--- Testing Boundary Limits ---")
    payload = generate_payload({"active_seconds": 5.0, "idle_seconds": 1.0})
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Time > 5.0s Status: {response.status_code}")
    
    payload = generate_payload({"active_seconds": -1.0, "idle_seconds": 6.0})
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Negative time Status: {response.status_code}")

    payload = generate_payload({"raw_signals": {"data": "x" * 10**6}})
    response = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"Excessive size Status: {response.status_code}")

def test_high_frequency():
    print("\n--- Testing High Frequency Calls ---")
    user_id = str(uuid.uuid4())
    success_count = 0
    fail_count = 0
    
    for i in range(10):
        payload = generate_payload({"user_id": user_id})
        response = requests.post(f"{BASE_URL}/ingest", json=payload, timeout=5)
        if response.status_code == 200:
            success_count += 1
        else:
            fail_count += 1
            
    print(f"High Frequency: {success_count} success, {fail_count} failures")

def test_lifecycle_and_regression():
    print("\n--- Testing Lifecycle and State Regression ---")
    user_id = str(uuid.uuid4())
    base_payload = generate_payload({"user_id": user_id, "cognitive_state": "ON_TASK"})
    
    response1 = requests.post(f"{BASE_URL}/ingest", json=base_payload, timeout=5)
    
    base_payload["cognitive_state"] = "AWAY"
    response2 = requests.post(f"{BASE_URL}/ingest", json=base_payload, timeout=5)
    
    print(f"Transition 1: {response1.status_code}, Transition 2: {response2.status_code}")
    
def test_deterministic_ids():
    print("\n--- Testing Deterministic IDs ---")
    payload1 = generate_payload()
    payload2 = payload1.copy()
    
    r1 = requests.post(f"{BASE_URL}/ingest", json=payload1, timeout=5)
    r2 = requests.post(f"{BASE_URL}/ingest", json=payload2, timeout=5)
    
    if r1.status_code == 200 and r2.status_code == 200:
        id1 = r1.json().get("packet_id")
        id2 = r2.json().get("packet_id")
        print(f"ID 1: {id1}")
        print(f"ID 2: {id2}")
        if id1 == id2:
            print("Deterministic IDs: YES")
        else:
            print("Deterministic IDs: NO")

if __name__ == "__main__":
    try:
        test_valid_submission()
        test_invalid_payloads()
        test_boundary_limits()
        test_high_frequency()
        test_lifecycle_and_regression()
        test_deterministic_ids()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        log_file.close()

