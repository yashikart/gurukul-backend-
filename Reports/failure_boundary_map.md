# Failure Boundary Map

**Date:** February 14, 2026  
**System:** Gurukul Backend  
**Purpose:** Identify hard failure points, silent failures, and long startup stages

---

## Executive Summary

| Category | Count | Severity | Status |
|----------|-------|----------|--------|
| Hard Failures | 4 | Critical | Documented |
| Silent Failures | 6 | Medium-High | Documented |
| Long Startup Stages | 2 | Medium | Documented |

---

## Hard Failure Points

### 1. Build Phase: Memory Limit Exceeded

**Location:** Render build container  
**Trigger:** Installing dependencies exceeds 512MB memory limit  
**Failure Mode:** Build process killed by OOM killer  
**Impact:** Deployment completely blocked  
**Current State:** Mitigated (torch/transformers removed)  
**Detection:** Build logs show "Killed" or "Out of memory"  
**Recovery:** Remove heavy dependencies, retry build  

**Prevention:**
- ✅ Heavy ML packages commented out in `requirements.txt`
- ✅ `--no-cache-dir` flag used to reduce memory
- ⚠️ Monitor: If new heavy dependencies added, build will fail

---

### 2. Build Phase: Dependency Installation Timeout

**Location:** `pip install` during build  
**Trigger:** Network timeout downloading packages  
**Failure Mode:** Build hangs or fails with timeout error  
**Impact:** Deployment blocked  
**Current State:** Possible but rare  
**Detection:** Build logs show timeout errors  
**Recovery:** Retry build, check network connectivity  

**Prevention:**
- ✅ `--no-cache-dir` reduces download size
- ⚠️ No explicit timeout configured (relies on Render defaults)

---

### 3. Boot Phase: Port Binding Failure

**Location:** `main.py` FastAPI initialization  
**Trigger:** Port already in use or permission denied  
**Failure Mode:** Server fails to start, no port binding  
**Impact:** Complete service failure  
**Current State:** Rare (Render manages ports)  
**Detection:** Startup logs show "Address already in use"  
**Recovery:** Render restarts container, or manual intervention  

**Prevention:**
- ✅ Render manages port allocation automatically
- ✅ FastAPI binds to `0.0.0.0:$PORT` (Render-provided port)

---

### 4. Database Phase: Invalid DATABASE_URL

**Location:** SQLAlchemy engine creation  
**Trigger:** `DATABASE_URL` malformed or missing  
**Failure Mode:** Database connection fails  
**Impact:** All database-dependent features fail  
**Current State:** Non-blocking (server starts anyway)  
**Detection:** Startup logs show connection errors  
**Recovery:** Fix `DATABASE_URL` in Render dashboard, restart  

**Prevention:**
- ⚠️ No validation before startup (connection attempted, fails gracefully)
- ✅ Server continues without DB (degraded mode)
- ⚠️ TODO: Add explicit validation with clear error message

---

## Silent Failures

### 1. Router Import Failure (Non-Critical)

**Location:** `startup_event()` → `import_other_routers_sync()`  
**Trigger:** Import error in router module (syntax error, missing dependency)  
**Failure Mode:** Router fails to import, error logged but startup continues  
**Impact:** Specific feature unavailable (e.g., chat, quiz, flashcards)  
**Detection:** Startup logs show `[Startup] ⚠️ Error importing other routers`  
**Current State:** Logged but not surfaced to health check  
**Recovery:** Fix import error, redeploy  

**Example:**
```python
# If chat router has import error:
[Startup] ⚠️ Error importing other routers: No module named 'app.routers.chat'
# Server still starts, but /api/v1/chat/* routes return 404
```

**Prevention:**
- ✅ Individual router failures don't block startup
- ⚠️ TODO: Add router health check endpoint
- ⚠️ TODO: Surface router failures in `/health` endpoint

---

### 2. Database Connection Timeout (Silent)

**Location:** SQLAlchemy connection pool  
**Trigger:** Database unreachable or slow to respond  
**Failure Mode:** Connection attempt times out (30s default), error logged  
**Impact:** Database-dependent features fail, but server continues  
**Detection:** Startup logs show connection timeout, but no user-visible error  
**Current State:** Logged but not surfaced  
**Recovery:** Check database status, network connectivity, restart  

**Prevention:**
- ✅ Connection timeout prevents indefinite hang
- ⚠️ TODO: Add database health check to `/health` endpoint
- ⚠️ TODO: Add retry logic with exponential backoff

---

### 3. External API Key Missing (Silent)

**Location:** Various routers (chat, quiz, TTS)  
**Trigger:** `GROQ_API_KEY` or `GEMINI_API_KEY` not set  
**Failure Mode:** Feature returns error when used, but startup succeeds  
**Impact:** Chat/quiz/TTS features fail at runtime  
**Detection:** Runtime errors when feature used, not at startup  
**Current State:** Runtime failure only  
**Recovery:** Add API key to Render environment variables  

**Prevention:**
- ⚠️ No startup validation of API keys
- ✅ Features fail gracefully with user-friendly error messages
- ⚠️ TODO: Add optional API key validation at startup (non-blocking)

---

### 4. CORS Configuration Missing (Silent)

**Location:** CORS middleware  
**Trigger:** Frontend URL not in `allow_origins`  
**Failure Mode:** Frontend requests blocked by CORS, but backend starts fine  
**Impact:** Frontend cannot communicate with backend  
**Detection:** Browser console shows CORS errors  
**Current State:** Hardcoded origins, may miss new frontend deployments  
**Recovery:** Add frontend URL to `allow_origins` in `main.py`  

**Prevention:**
- ✅ Production frontend URL hardcoded
- ⚠️ TODO: Make CORS origins configurable via env var
- ⚠️ TODO: Add CORS validation to health check

---

### 5. PRANA Bucket Connection Failure (Silent)

**Location:** PRANA telemetry ingestion  
**Trigger:** Bucket service unreachable or misconfigured  
**Failure Mode:** PRANA packets fail to ingest, error logged but server continues  
**Impact:** Telemetry data lost, but core features work  
**Detection:** PRANA logs show connection failures  
**Current State:** Non-blocking, graceful degradation  
**Recovery:** Check bucket service status, verify configuration  

**Prevention:**
- ✅ PRANA has 10s timeout, 3 retries, offline queue
- ✅ PRANA failures don't affect core features
- ✅ Kill switch available: `window.PRANA_DISABLED = true`

---

### 6. Redis Connection Failure (Silent)

**Location:** Redis client initialization (if used)  
**Trigger:** Redis unreachable or misconfigured  
**Failure Mode:** Falls back to in-memory storage, error logged  
**Impact:** Session/cache data lost on restart, but server continues  
**Detection:** Startup logs show Redis connection errors  
**Current State:** Graceful fallback to memory  
**Recovery:** Check Redis service, verify connection string  

**Prevention:**
- ✅ Fallback to in-memory storage
- ✅ Non-blocking initialization

---

## Long Startup Stages

### 1. Build Phase: 5-10 Minutes

**Location:** Dependency installation  
**Duration:** 5-10 minutes (reduced from 40-50 min after removing ML packages)  
**Bottleneck:** Network download speed, package compilation  
**Impact:** Every deployment requires full rebuild  
**Mitigation:**
- ✅ Removed heavy ML packages (torch, transformers)
- ✅ Using `--no-cache-dir` to reduce memory
- ⚠️ Still slow due to network and Python package installation

**Optimization Opportunities:**
- Use Docker image with pre-installed dependencies
- Use Render's build cache (if available)
- Split into multiple services (build once, deploy many)

---

### 2. Router Import Phase: 5-15 Seconds

**Location:** `startup_event()` → router imports  
**Duration:** 5-15 seconds total (auth: 2-5s, others: 3-10s)  
**Bottleneck:** Python import time, module initialization  
**Impact:** First request may be slow if routers not yet loaded  
**Mitigation:**
- ✅ Routers import AFTER port binding (non-blocking)
- ✅ Auth router prioritized (30s timeout)
- ✅ Other routers can load in background

**Optimization Opportunities:**
- Lazy import routers on first request (trade-off: first request slower)
- Pre-compile Python bytecode
- Reduce router complexity

---

## Failure Boundary Matrix

| Failure Point | Hard/Silent | Blocks Startup? | Blocks Feature? | Recovery Time |
|---------------|-------------|-----------------|-----------------|---------------|
| Build OOM | Hard | ✅ Yes | N/A | 5-10 min (retry) |
| Build Timeout | Hard | ✅ Yes | N/A | 5-10 min (retry) |
| Port Binding | Hard | ✅ Yes | N/A | <1 min (restart) |
| Invalid DB URL | Hard | ❌ No | ✅ Yes (DB features) | <1 min (fix env) |
| Router Import | Silent | ❌ No | ✅ Yes (that router) | 5-10 min (redeploy) |
| DB Timeout | Silent | ❌ No | ✅ Yes (DB features) | <1 min (check DB) |
| Missing API Key | Silent | ❌ No | ✅ Yes (that feature) | <1 min (add env) |
| CORS Misconfig | Silent | ❌ No | ✅ Yes (frontend) | <1 min (fix code) |
| PRANA Failure | Silent | ❌ No | ❌ No (non-critical) | N/A (graceful) |
| Redis Failure | Silent | ❌ No | ⚠️ Partial (cache) | <1 min (check Redis) |

---

## Detection and Monitoring

### Current Detection Methods

1. **Build Failures:** Render build logs
2. **Startup Failures:** Render runtime logs (look for `[Startup] ✗`)
3. **Runtime Failures:** Application logs, error responses
4. **Silent Failures:** Manual log inspection required

### Recommended Monitoring

1. **Health Check Endpoint:** `/health` (exists but basic)
2. **Readiness Check:** TODO - separate endpoint for readiness
3. **Router Health:** TODO - endpoint to check router status
4. **Database Health:** TODO - endpoint to check DB connectivity
5. **External API Health:** TODO - endpoint to check API key validity

---

## Recovery Procedures

### Hard Failure Recovery

1. **Build OOM:**
   ```bash
   # Remove heavy dependencies from requirements.txt
   # Commit and push
   git commit -m "Remove heavy dependencies"
   git push origin main
   ```

2. **Port Binding Failure:**
   ```bash
   # Render automatically restarts
   # Or manually restart in Render dashboard
   ```

3. **Database Connection Failure:**
   ```bash
   # Fix DATABASE_URL in Render dashboard
   # Restart service
   ```

### Silent Failure Recovery

1. **Router Import Failure:**
   ```bash
   # Check logs for import errors
   # Fix import issue in code
   # Redeploy
   ```

2. **Database Timeout:**
   ```bash
   # Check database status
   # Verify network connectivity
   # Restart service
   ```

3. **Missing API Key:**
   ```bash
   # Add API key to Render environment variables
   # Restart service
   ```

---

## Prevention Checklist

- [x] Heavy dependencies removed from requirements.txt
- [x] Non-blocking startup implemented
- [x] Graceful degradation for non-critical services
- [ ] Database health check added
- [ ] Router health check added
- [ ] API key validation added (non-blocking)
- [ ] CORS configuration made dynamic
- [ ] Startup metrics/logging enhanced
- [ ] Automated failure detection/alerts

---

## Next Steps

1. Add comprehensive health checks for all components
2. Implement startup metrics to track timing
3. Add automated failure detection and alerts
4. Create runbook for common failure scenarios
5. Implement circuit breakers for external dependencies
