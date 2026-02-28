import sys
import threading
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, engine
from app.services.deterministic_repo import deterministic_repo
from app.models.prana_models import PranaPacket

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def worker(i):
    db = SessionLocal()
    try:
        packet_data = {
            "packet_id": str(uuid.uuid4()),
            "user_id": f"test_user_{i}",
            "system_type": "gurukul",
            "role": "student",
            "client_timestamp": datetime.datetime.utcnow().isoformat(),
            "cognitive_state": "ON_TASK",
            "active_seconds": 5.0,
            "idle_seconds": 0.0,
            "away_seconds": 0.0,
            "focus_score": 95.0,
            "raw_signals": {},
            "processed_by_karma": False
        }
        deterministic_repo.add_packet(db, packet_data)
        print(f"Worker {i} success")
    except Exception as e:
        print(f"Worker {i} failed: {e}")
    finally:
        db.close()

def run_concurrent_test():
    print("Running Concurrent Ledger Test...")
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

    # Now verify
    db = SessionLocal()
    result = deterministic_repo.verify_packet_chain(db)
    with open("test_ledger_output.txt", "w") as f:
        f.write(str(result))
    db.close()

if __name__ == "__main__":
    run_concurrent_test()
