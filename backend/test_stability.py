import requests
import time

def test_sequential(total=50):
    url = "http://localhost:3000/api/v1/tts/vaani"
    payload = {"text": "Sequential stability test request.", "language": "en"}
    success = 0
    start_all = time.time()
    
    for i in range(total):
        try:
            start = time.time()
            # Adding a bit of variation to the text to test caching and load
            payload["text"] = f"Sequential stability test request iteration {i}."
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                success += 1
            print(f"Req {i}: Status {response.status_code} in {time.time() - start:.2f}s")
        except Exception as e:
            print(f"Req {i}: Failed with {e}")
    
    print(f"Total: {success}/{total} successful in {time.time() - start_all:.2f}s")

if __name__ == "__main__":
    print("Starting 50 Consecutive Requests Stability Test...")
    test_sequential(50)
