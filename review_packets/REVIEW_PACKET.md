# REVIEW PACKET (UPDATED)
## Gurukul Backend — Handover Verification Document

---

## 1. SYSTEM STATUS AT HANDOVER

**Date:** 2026-05-07  
**Backend Version:** v2 (Deterministic Mode)  
**Production URL:** https://gurukul-up9j.onrender.com  
**Frontend URL:** https://gurukul.blackholeinfiverse.com  
**Test Result:** APPROVED WITH MINOR FIXES (BHIV Protocol v2, 8/9 phases passed)

---

## 2. WHAT IS OPERATIONAL

| Component | Status | Notes |
|-----------|--------|-------|
| Auth (register/login) | ✅ Working | JWT, bcrypt, STUDENT-only |
| Chat (Groq LLM) | ✅ Working | RAG optional |
| TTS (3-tier fallback) | ✅ Working | Vaani → OpenAI → gTTS |
| STT (Groq Whisper) | ✅ Working | faster-whisper fallback |
| Flashcards | ✅ Working | AI generation + spaced repetition |
| Quiz | ✅ Working | AI generation + scoring |
| Learning notes | ✅ Working | Groq + YouTube recommendations |
| Karma Tracker | ✅ Working | Requires MongoDB |
| EMS Sync | ⚠️ Depends on EMS | Must have EMS_API_BASE_URL |
| Vector Store/RAG | ⚠️ Disabled in prod | Memory limit; works in dev |
| Vaani XTTS | ⚠️ Optional | Requires vaani-engine to be running |
| Multi-tenant | ⚠️ Disabled | Set MULTI_TENANT_ENABLED=true to enable |
| /system/health | ❌ Minor miss | system_monitor router sometimes doesn't load |

---

## 3. KNOWN ISSUES

1. **`/system/health` returns 404** — `system_monitor` router not registering on Render. Non-critical: use `/` for liveness and `/system/metrics` for metrics.

2. **Chat history is in-memory** — Server restart wipes all conversation history. For production, this should be persisted in PostgreSQL.

3. **Vector store disabled in prod** — `sentence-transformers` and `chromadb` are too heavy for 512MB Render instance. RAG falls back to Groq-only.

4. **No refresh token** — JWT expires after 7 days. User must log in again. No refresh mechanism implemented.

5. **EMS auto-create is off** — `EMS_AUTO_CREATE_STUDENTS=false` by default to prevent signup slowdowns. Enable carefully.

---

## 4. HANDOVER CHECKLIST

- [x] SYSTEM_OVERVIEW.md — full architecture documented
- [x] API_GUIDE.md — all endpoints documented with input/output examples
- [x] DB_GUIDE.md — all tables, relationships, and failure modes documented
- [x] ENV_SETUP.md — complete .env template and setup instructions
- [x] DEBUG_GUIDE.md — issue-by-issue debug playbook
- [x] FAQ.md — 40 questions covering all aspects of the system
- [x] REVIEW_PACKET.md (this file) — updated with current status

---

## 5. RECEIVER RESPONSIBILITIES

**Soham Kotkar (Runtime + TANTRA):**
- Verify PRAVAH_URL and BUCKET_URL are set correctly for production
- Monitor `runtime_events.json` for TANTRA debug signals
- Handle `x-trace-id` propagation to TANTRA systems
- Ensure ServiceWatchdog restart limits (3 max) are understood

**Alay Patel (DevOps/Infra):**
- Ensure DATABASE_URL points to PostgreSQL (not SQLite) in production
- Set JWT_SECRET_KEY to a strong random value
- Configure MongoDB for Karma tracker
- Set up health monitoring on `/` and `/system/metrics`
- Ensure Render has all env vars from ENV_SETUP.md

---

## 6. CRITICAL THINGS NOT TO BREAK

1. **Do not change JWT_SECRET_KEY in production** — invalidates all active sessions
2. **Do not delete PRANA tables** — append-only by design
3. **Do not mount a new router without fault-isolation** — follow the try/except pattern in `main.py` startup event
4. **Do not remove bcrypt** — all passwords will be unverifiable

---

## 7. ENTRY POINTS QUICK REFERENCE

```
# Health check
GET /

# Swagger docs
GET /docs

# Metrics
GET /system/metrics

# Auth
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me

# Chat
POST /api/v1/chat

# TTS
POST /api/v1/agent/tts
POST /api/v1/tts/speak

# STT
POST /api/v1/voice/listen

# Karma
GET /api/v1/karma/balance/{user_id}
```

---

## 8. ORIGINAL BHIV TEST RESULTS

From BHIV Universal Testing Protocol v2 (2026-04-23):

| Phase | Status |
|-------|--------|
| P1 — System Access | PARTIAL PASS |
| P2 — User Flow | PASS |
| P3 — Trace Continuity | PASS |
| P4 — CI/CD | PASS |
| P5 — Failure Injection | PASS |
| P6 — Multi-User | PASS |
| P7 — Metrics | PASS |
| P8 — Stream | PASS |
| P9 — Correlation | PASS |

**272 requests, 0 errors, 0.0% error rate**

---

## 9. TO RUN THIS SYSTEM FROM SCRATCH

```bash
# 1. Clone
git clone https://github.com/yashikart/gurukul-backend-.git
cd gurukul-backend

# 2. Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your GROQ_API_KEY, DATABASE_URL, JWT_SECRET_KEY, MONGO_URI

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Start
uvicorn app.main:app --host 0.0.0.0 --port 3000

# 5. Verify
curl http://localhost:3000/
# Should return: {"message": "Gurukul Backend API v2 is running", "docs": "/docs"}
```

Full instructions in `ENV_SETUP.md`.
