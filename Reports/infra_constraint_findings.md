# Infrastructure Constraint Findings

**Test Date:** February 7, 2026  
**Environment:** Render Free Tier + Vercel  
**Tester:** Soham Kotkar (Code Analysis by AI Assistant)  
**Status:** CODE ANALYSIS COMPLETE - TIMEOUT HANDLING IMPROVED - MANUAL TESTING REQUIRED

---

## Executive Summary

**Infrastructure Readiness:** ⚠️ CONDITIONAL  
**Free-Tier Impact:** ⚠️ HIGH (Cold starts expected)  
**Cold Start Issues:** ✅ MITIGATED (Retry logic exists)  
**Timeout Risks:** ✅ HANDLED (30-60s timeouts with retry)

**Key Finding:** Code has excellent infrastructure handling with explicit timeouts added. Cold starts will cause delays. Pre-warming recommended for demo.

---

## Render Free Tier Constraints

### Cold Start Behavior

**Observation:** Render free tier spins down after 15 minutes of inactivity.

| Endpoint | Cold Start Time | Warm Response Time | User Impact | Demo Risk |
|----------|----------------|-------------------|-------------|-----------|
| /api/v1/chat | 30-60s (expected) | <3s | HIGH (long wait) | ⚠️ HIGH |
| /api/v1/subjects | 30-60s (expected) | <2s | MEDIUM | ⚠️ MEDIUM |
| /api/v1/learning/explore | 30-60s (expected) | <3s | HIGH | ⚠️ HIGH |
| /api/v1/quiz/generate | 30-60s (expected) | <4s | HIGH | ⚠️ HIGH |
| /api/v1/tts/speak | 30-60s (expected) | <2s | MEDIUM | ⚠️ MEDIUM |
| /api/v1/tts/vaani | 30-60s (expected) | <2s | MEDIUM | ⚠️ MEDIUM |

**First Request After Idle:**
- Idle Duration: 15+ minutes
- First Request Time: 30-60 seconds (Render free tier)
- Timeout Occurred: NO (code has 30s, 40s, 50s, 60s retry logic)
- User Experience: Long loading state, but retry logic prevents failure

**Mitigation Found in Code:**
- `AuthContext.jsx`: Exponential backoff retry (30s, 40s, 50s, 60s timeouts)
- `apiClient.js`: Retry logic for network errors
- User sees loading state, not error (GOOD) 

### Memory Constraints

| Operation | Memory Used | Memory Limit | Status | Demo Risk |
|-----------|-------------|--------------|--------|-----------|
| App startup | Unknown | 512 MB | ⚠️ NEEDS TESTING | ⚠️ MEDIUM |
| Chat request | Unknown | 512 MB | ⚠️ NEEDS TESTING | ⚠️ LOW |
| TTS generation | Unknown | 512 MB | ⚠️ NEEDS TESTING | ⚠️ LOW |
| Quiz generation | Unknown | 512 MB | ⚠️ NEEDS TESTING | ⚠️ MEDIUM |

**Note:** Cannot determine actual memory usage from code. Manual testing required.

### Database (SQLite) Constraints

| Test | Result | Impact | Demo Risk |
|------|--------|--------|-----------|
| Concurrent reads | ⚠️ NEEDS TESTING | Unknown | ⚠️ LOW |
| Concurrent writes | ⚠️ NEEDS TESTING | Unknown | ⚠️ MEDIUM |
| Large query (>1000 rows) | ⚠️ NEEDS TESTING | Unknown | ⚠️ LOW |
| Connection timeout | ⚠️ NEEDS TESTING | Unknown | ⚠️ MEDIUM |

**Note:** SQLite is file-based, may have locking issues with concurrent writes. Manual testing required.

---

## Vercel Constraints

### Function Execution Limits

| Metric | Limit | Observed | Status |
|--------|-------|----------|--------|
| Max execution time | 10s (Hobby) | ⚠️ NEEDS TESTING | ⚠️ LOW RISK |
| Payload size | 4.5 MB | ⚠️ NEEDS TESTING | ⚠️ LOW RISK |
| Concurrent builds | 1 | N/A (static site) | ✅ N/A |

**Note:** Frontend is static (React SPA), not serverless functions, so execution limits don't apply.

### Cold Start (Frontend)

| Scenario | First Load Time | Cached Load Time | Status |
|----------|-----------------|------------------|--------|
| Homepage | | | |
| Dashboard | | | |
| Chat page | | | |
| Quiz page | | | |

---

## Network Performance

### Latency Tests

**From Local Machine:**

| Endpoint | Min | Max | Avg | Status |
|----------|-----|-----|-----|--------|
| /api/v1/chat | | | | |
| /api/v1/subjects | | | | |
| /api/v1/lessons | | | | |
| /api/v1/tts/speak | | | | |

**Simulated Slow 3G:**

| Endpoint | Load Time | Timeout? | Demo Risk |
|----------|-----------|----------|-----------|
| Homepage | | | |
| Dashboard | | | |
| Chat | | | |
| TTS | | | |

---

## Timeout Scenarios

### API Timeouts

| Endpoint | Timeout After | Actual Response | Behavior | Demo Risk |
|----------|---------------|-----------------|----------|-----------|
| Chat | 60s (explicit), then retries | ✅ Explicit timeout + retries | ✅ Graceful | ✅ LOW |
| TTS | 30s (explicit), then retries | ✅ Explicit timeout + retries | ✅ Graceful | ✅ LOW |
| Quiz Gen | 30s (first), 40s, 50s, 60s (retries) | ✅ Retries with backoff | ✅ Graceful | ✅ LOW |
| Subject Load | 30s (first), 40s, 50s, 60s (retries) | ✅ Retries with backoff | ✅ Graceful | ✅ LOW |

**Timeout Handling:**
- Does it show error message? ✅ YES (via handleApiError)
- Does it allow retry? ✅ YES (automatic retry with exponential backoff)
- Does it crash the app? ✅ NO (errors caught and handled gracefully)

---

## Error Rate Analysis

### 5xx Errors

| Endpoint | Error Code | Frequency | Trigger | Demo Risk |
|----------|------------|-----------|---------|-----------|
| | | | | |

### 4xx Errors

| Endpoint | Error Code | Frequency | Trigger | Demo Risk |
|----------|------------|-----------|---------|-----------|
| | | | | |

---

## Resource Limits Hit

### Rate Limiting

| Endpoint | Limit | Tested At | Blocked? | Demo Risk |
|----------|-------|-----------|----------|-----------|
| Chat | | | | |
| TTS | | | | |
| Quiz | | | | |

### Bandwidth

| Resource | Size | Load Time | Demo Risk |
|----------|------|-----------|-----------|
| Main bundle | | | |
| Images | | | |
| Audio files | | | |

---

## Concurrent User Testing

### Simultaneous Sessions

| # Users | Login Success | Chat Works | Quiz Works | TTS Works | Status |
|---------|---------------|------------|------------|-----------|--------|
| 2 | | | | | |
| 5 | | | | | |
| 10 | | | | | |

---

## Free-Tier Specific Risks

### Demo Day Risks

| Risk | Likelihood | Impact | Mitigation | Demo Risk |
|------|------------|--------|------------|-----------|
| Backend sleeping | HIGH | HIGH | ✅ Keep-alive ping OR pre-warm | ⚠️ HIGH |
| Cold start delay | HIGH | MEDIUM | ✅ Retry logic exists | ⚠️ MEDIUM |
| Memory crash | MEDIUM | HIGH | ⚠️ Unknown (needs testing) | ⚠️ MEDIUM |
| DB lock | LOW | HIGH | ⚠️ SQLite limits | ⚠️ LOW |
| Rate limiting | LOW | MEDIUM | ⚠️ Unknown | ⚠️ LOW |

### Keep-Alive Strategy

**Current Implementation:**
- Is there a keep-alive ping? ⚠️ NOT FOUND IN CODE
- Frequency: N/A
- Effectiveness: N/A

**Recommendation:**
- Implement keep-alive ping every 10 minutes OR
- Pre-warm backend 5 minutes before demo
- Show "Waking up server..." message during cold start 

**Recommendation:**

---

## Failover Behavior

### When Backend is Down

| Component | Expected | Actual | Demo Risk |
|-----------|----------|--------|-----------|
| Homepage | | | |
| Dashboard | | | |
| Chat | | | |
| TTS | | | |

### When Database is Locked

| Component | Expected | Actual | Demo Risk |
|-----------|----------|--------|-----------|
| Login | | | |
| Data fetch | | | |
| Data save | | | |

---

## Monitoring Gaps

| Metric | Monitored? | Alert? | Demo Risk |
|--------|------------|--------|-----------|
| Response time | | | |
| Error rate | | | |
| Cold start count | | | |
| Memory usage | | | |
| DB locks | | | |

---

## Recommendations

### Immediate (Before Demo):
1. 

### Short-term:
1. 

### Long-term:
1. 

---

## Infrastructure Demo Readiness: ⚠️ CONDITIONAL

**Blockers:**
- Backend cold start delays (30-60s) - mitigated by retry logic but still noticeable
- No keep-alive ping found in code
- Memory usage unknown (needs testing)

**Workarounds in Place:**
- ✅ Retry logic with exponential backoff (30s, 40s, 50s, 60s)
- ✅ Graceful error handling
- ✅ User-friendly error messages
- ⚠️ Need to add: Keep-alive ping OR pre-warm before demo

**Confidence Level:** ⬜ High / ✅ Medium / ⬜ Low

**Recommendation:** Pre-warm backend 5 minutes before demo OR implement keep-alive ping

---

**Last Updated:**  
**Next Review:**
