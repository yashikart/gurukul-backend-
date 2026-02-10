# Infrastructure Constraint Findings

**Test Date:** February 2026  
**Environment:** Render Free Tier + Vercel  
**Tester:** Soham Kotkar  
**Status:** IN PROGRESS

---

## Executive Summary

**Infrastructure Readiness:** ⬜ TBD  
**Free-Tier Impact:** ⬜ TBD  
**Cold Start Issues:** ⬜ TBD  
**Timeout Risks:** ⬜ TBD

---

## Render Free Tier Constraints

### Cold Start Behavior

**Observation:** Render free tier spins down after 15 minutes of inactivity.

| Endpoint | Cold Start Time | Warm Response Time | User Impact | Demo Risk |
|----------|----------------|-------------------|-------------|-----------|
| /api/v1/chat | | | | |
| /api/v1/subjects | | | | |
| /api/v1/lessons | | | | |
| /api/v1/questions | | | | |
| /api/v1/tts/speak | | | | |

**First Request After Idle:**
- Idle Duration: 
- First Request Time: 
- Timeout Occurred: YES / NO
- User Experience: 

### Memory Constraints

| Operation | Memory Used | Memory Limit | Status | Demo Risk |
|-----------|-------------|--------------|--------|-----------|
| App startup | | 512 MB | | |
| Chat request | | 512 MB | | |
| TTS generation | | 512 MB | | |
| Quiz generation | | 512 MB | | |

### Database (SQLite) Constraints

| Test | Result | Impact | Demo Risk |
|------|--------|--------|-----------|
| Concurrent reads | | | |
| Concurrent writes | | | |
| Large query (>1000 rows) | | | |
| Connection timeout | | | |

---

## Vercel Constraints

### Function Execution Limits

| Metric | Limit | Observed | Status |
|--------|-------|----------|--------|
| Max execution time | 10s (Hobby) | | |
| Payload size | 4.5 MB | | |
| Concurrent builds | 1 | | |

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
| Chat | 30s | | | |
| TTS | 30s | | | |
| Quiz Gen | 30s | | | |
| Subject Load | 30s | | | |

**Timeout Handling:**
- Does it show error message? YES / NO
- Does it allow retry? YES / NO
- Does it crash the app? YES / NO

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
| Backend sleeping | HIGH | HIGH | Keep-alive ping | |
| Cold start delay | HIGH | MEDIUM | Pre-warm | |
| Memory crash | MEDIUM | HIGH | Optimize | |
| DB lock | LOW | HIGH | SQLite limits | |
| Rate limiting | LOW | MEDIUM | Throttle | |

### Keep-Alive Strategy

**Current Implementation:**
- Is there a keep-alive ping? YES / NO
- Frequency: 
- Effectiveness: 

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

## Infrastructure Demo Readiness: YES / NO

**Blockers:**
- 

**Workarounds in Place:**
- 

**Confidence Level:** ⬜ High / ⬜ Medium / ⬜ Low

---

**Last Updated:**  
**Next Review:**
