import time
import requests
import subprocess
import os
import signal
import sys

# Configuration
CHECK_INTERVAL = 30  # Seconds
HEALTH_URL = "http://localhost:3000/system/health"
MAX_FAILURES = 3

def restart_backend():
    print("[Watchdog] CRITICAL: Backend unresponsive. Attempting restart...")
    # Logic to find and kill existing process if any
    # Then start fresh
    # subprocess.Popen(["python", "-m", "app.main"])

def monitor_loop():
    consecutive_failures = 0
    print(f"[Watchdog] Monitoring {HEALTH_URL}...")
    
    while True:
        try:
            response = requests.get(HEALTH_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                if status == "healthy":
                    consecutive_failures = 0
                else:
                    print(f"[Watchdog] WARN: System status: {status}")
                    consecutive_failures += 1
            else:
                consecutive_failures += 1
        except Exception as e:
            print(f"[Watchdog] Error reaching backend: {e}")
            consecutive_failures += 1
        
        if consecutive_failures >= MAX_FAILURES:
            restart_backend()
            consecutive_failures = 0
            time.sleep(60) # Give it time to boot
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        print("[Watchdog] Stopping...")
        sys.exit(0)
