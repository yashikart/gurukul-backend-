# Deployment Flow Documentation

**Date:** February 14, 2026  
**System:** Gurukul Backend  
**Platform:** Render.com  
**Purpose:** End-to-end deployment flow documentation for reliability and repeatability

---

## Overview

This document maps the complete deployment flow from code push to first request readiness, identifying each stage, dependencies, and timing expectations.

---

## Stage 1: Build Phase

### Trigger
- **Git push to `main` branch** OR manual deploy trigger in Render dashboard
- Render detects changes via webhook or manual trigger

### Process
1. **Environment Setup**
   - Render spins up build container
   - Python 3.11+ environment initialized
   - Working directory: `/opt/render/project/src`

2. **Dependency Installation**
   - Reads `requirements.txt` from `backend/` directory
   - Executes: `pip install --no-cache-dir -r requirements.txt`
   - **Expected Duration:** 5-10 minutes (reduced from 40-50 min after removing torch/transformers)
   - **Critical Dependencies:**
     - FastAPI, Uvicorn (core server)
     - SQLAlchemy, psycopg2-binary (database)
     - python-jose (auth)
     - groq, gtts (AI/TTS)
   - **Disabled Dependencies (memory constraints):**
     - torch, transformers, sentence-transformers (commented out)
     - ChromaDB, Qdrant, Weaviate, Pinecone (commented out)

3. **Build Validation**
   - Checks for syntax errors
   - Validates Python imports
   - **Failure Points:**
     - Missing dependencies → Build fails
     - Syntax errors → Build fails
     - Memory limit exceeded → Build fails (512MB limit)

### Build Output
- Compiled Python bytecode
- Installed packages in virtual environment
- **Artifact:** Ready-to-run Python environment

---

## Stage 2: Boot Phase

### Trigger
- Build completes successfully
- Render starts runtime container

### Process
1. **Container Initialization**
   - Runtime container starts
   - Environment variables loaded from Render dashboard
   - **Required Env Vars:**
     - `DATABASE_URL` (PostgreSQL connection string)
     - `SECRET_KEY` (JWT signing key)
     - `FRONTEND_URL` (CORS origin)
     - `GROQ_API_KEY` (optional, for chat/quiz)
     - `PORT` (auto-set by Render, typically 10000)

2. **Python Process Start**
   - Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Working directory: `/opt/render/project/src/backend`
   - **Expected Duration:** <5 seconds to port binding

3. **FastAPI App Initialization**
   - `main.py` loads immediately
   - FastAPI app created: `app = FastAPI(title=settings.API_TITLE)`
   - CORS middleware configured
   - **Critical:** App binds to port BEFORE router imports (non-blocking startup)

### Boot Output
- Server listening on port (typically 10000)
- FastAPI app instance ready
- **Status:** Server accepts connections but routers not yet loaded

---

## Stage 3: Database Connection Phase

### Trigger
- Server bound to port
- Startup event begins

### Process
1. **Database Engine Creation**
   - SQLAlchemy engine initialized from `DATABASE_URL`
   - Connection pool created (default: 5 connections)
   - **Expected Duration:** 2-5 seconds
   - **Failure Points:**
     - Invalid `DATABASE_URL` → Connection fails, logged but non-blocking
     - Database unreachable → Connection timeout (30s), logged but non-blocking
     - Wrong credentials → Authentication fails, logged but non-blocking

2. **Connection Validation**
   - Test query executed: `SELECT 1`
   - **Current Status:** Validation exists but non-blocking
   - **TODO:** Add explicit validation with timeout

3. **Schema Check**
   - SQLAlchemy checks table existence
   - Migrations handled by Alembic (if configured) OR manual schema creation
   - **Current Status:** No automatic migrations; schema must exist

### Database Output
- Connection pool ready (or failed gracefully)
- **Status:** Database available OR degraded mode (non-critical features disabled)

---

## Stage 4: Migrations Phase

### Current Status
- **No automatic migrations configured**
- Schema must be pre-created manually
- Alembic not integrated

### Manual Migration Process (if needed)
1. Connect to database via Render dashboard or CLI
2. Run SQL scripts manually
3. Verify schema exists

### Future Migration Flow (recommended)
1. Alembic detects pending migrations
2. Executes migrations automatically
3. Validates schema version
4. **Expected Duration:** 10-30 seconds (depending on migration count)

---

## Stage 5: Router Import Phase

### Trigger
- Startup event begins after port binding
- Non-blocking import strategy

### Process
1. **Critical Router: Auth (30s timeout)**
   - `import_auth_router_sync()` executed in thread
   - Imports `app.routers.auth`
   - Registers routes: `/api/v1/auth/*`
   - **Expected Duration:** 2-5 seconds
   - **Failure Handling:** Logged but startup continues

2. **Non-Critical Routers (120s timeout)**
   - `import_other_routers_sync()` executed in background thread
   - Imports: chat, flashcards, learning, ems, quiz, tts, bucket, etc.
   - **Expected Duration:** 5-15 seconds total
   - **Failure Handling:** Individual router failures logged, others continue

3. **Karma Tracker Routers**
   - Imported after other routers
   - Routes: `/api/v1/karma/*`
   - **Expected Duration:** 3-8 seconds
   - **Failure Handling:** Logged but non-blocking

### Router Import Output
- All routers registered (or partial registration if some fail)
- Routes available at `/api/v1/*` endpoints
- **Status:** Full API surface ready OR degraded mode

---

## Stage 6: First Request Readiness

### Trigger
- All startup events complete
- Server fully initialized

### Readiness Criteria
1. **Port Binding:** ✅ Server listening on port
2. **Health Endpoint:** ✅ `/health` returns `{"status": "healthy"}`
3. **Auth Endpoint:** ✅ `/api/v1/auth/login` responds (even if DB fails)
4. **CORS:** ✅ Frontend can make requests

### First Request Flow
1. Client sends request to `/health` or `/api/v1/auth/login`
2. FastAPI routes request to appropriate router
3. Router processes request (may hit DB, external APIs)
4. Response returned to client

### Expected Timing
- **Cold Start (first deploy):** 30-60 seconds total
  - Build: 5-10 min
  - Boot: <5s
  - DB connection: 2-5s
  - Router imports: 5-15s
  - **Total:** ~6-11 minutes (mostly build time)

- **Warm Start (subsequent deploys):** 10-20 seconds total
  - Build: 5-10 min (still required)
  - Boot: <5s
  - DB connection: 1-3s (pooled)
  - Router imports: 3-10s
  - **Total:** ~6-11 minutes (build dominates)

- **After Build (runtime restart):** 10-20 seconds
  - Boot: <5s
  - DB connection: 1-3s
  - Router imports: 3-10s
  - **Total:** ~10-20 seconds

---

## Deployment Flow Summary

```
┌─────────────────┐
│  Git Push/Trigger│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Build Phase   │ 5-10 min
│  (Dependencies) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Boot Phase    │ <5s
│  (Port Binding) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DB Connection  │ 2-5s
│   (Non-blocking)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Router Imports  │ 5-15s
│  (Non-blocking) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ First Request   │ Ready
│    Ready        │
└─────────────────┘
```

---

## Key Design Decisions

1. **Non-Blocking Startup:** Routers import AFTER port binding, allowing server to accept requests even if some routers fail
2. **Graceful Degradation:** Database failures don't prevent server from starting
3. **Timeout Protection:** Auth router has 30s timeout, others have 120s timeout
4. **Memory Optimization:** Heavy ML dependencies removed to stay within 512MB limit

---

## Verification Commands

```bash
# Check build logs
# Render Dashboard → Deploys → Latest → Build Logs

# Check startup logs
# Render Dashboard → Deploys → Latest → Runtime Logs
# Look for: "[Startup] ✓ Auth router registered"

# Test health endpoint
curl https://gurukul-backend-kap2.onrender.com/health

# Test first request
curl -X POST https://gurukul-backend-kap2.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

---

## Next Steps

1. Add explicit database validation with timeout
2. Integrate Alembic for automatic migrations
3. Add startup metrics/logging for each phase
4. Implement health check that validates DB connectivity
5. Add readiness probe endpoint separate from health check
