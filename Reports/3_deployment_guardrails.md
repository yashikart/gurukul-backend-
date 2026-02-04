# Deployment Guardrails

## Add Health Check (TODO)

Add to `backend/app/main.py`:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "auth_ready": auth is not None}
```

Add to `render.yaml`:
```yaml
healthCheckPath: /health
```

## Memory Guards

**Current memory usage:** ~300-400 MB  
**Render limit:** 512 MB  
**Headroom:** ~100-200 MB

**To reduce memory:**
```bash
# Comment these in requirements.txt:
# torch>=2.0.0
# transformers>=4.30.0
# sentence-transformers>=2.7.0
```

## Startup Timeouts

Already configured in `main.py`:
- Auth router: 30s timeout
- Other routers: 120s timeout (reduce to 60s)

## PRANA Guardrails (Active)

| Guard                       | Status    |
|-----------------------------|-----------|
| 10-second fetch timeout     | ✅ Active |
| 3 retries with backoff      | ✅ Active |
| Offline queue (100 packets) | ✅ Active |
| Redis fallback to memory    | ✅ Active |
| Kill switch available       | ✅ Ready  |

## Database Validation (TODO)

Add to startup:
```python
async def validate_database():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except:
        print("[Startup] ✗ Database FAILED")
        return False
```

## Retry Policy

| Component       | Retry | Reason                          |
|-----------------|-------|---------------------------------|
| PRANA → Backend | 3x    | Telemetry can retry             |
| Auth requests   | 0x    | User expects immediate feedback |
| DB connections  | 3x    | Transient failures common       |

