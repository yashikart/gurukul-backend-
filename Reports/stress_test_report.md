# Stress Test Report

**Date:** February 14, 2026  
**System:** Gurukul Backend  
**Purpose:** Controlled stress tests - concurrent users, auth load, quiz/chat/lesson access

---

## Executive Summary

| Test Category | Status | Results |
|---------------|--------|---------|
| Concurrent Users | ⚠️ Simulated | See below |
| Auth Load | ⚠️ Simulated | See below |
| Quiz Access | ⚠️ Simulated | See below |
| Chat Access | ⚠️ Simulated | See below |
| Lesson Access | ⚠️ Simulated | See below |

**Note:** This report documents stress test methodology and expected behavior. Actual stress tests should be run in staging/production environment.

---

## Test Environment

### Configuration

- **Platform:** Render.com (Free Tier)
- **Memory Limit:** 512 MB
- **CPU:** Limited (Free Tier)
- **Database:** PostgreSQL (Render managed)
- **Endpoint:** `https://gurukul-backend-kap2.onrender.com`

### Test Tools

- **Load Testing:** `curl`, `ab` (Apache Bench), or `wrk`
- **Monitoring:** Render logs, application logs
- **Metrics:** Response time, error rate, throughput

---

## Test 1: Concurrent Users

### Objective

Test system behavior under concurrent user load.

### Test Parameters

- **Concurrent Users:** 10, 25, 50, 100
- **Duration:** 60 seconds per test
- **Endpoint:** `GET /health`
- **Expected:** All requests succeed, response time <500ms

### Test Script

```bash
# Test with 10 concurrent users
ab -n 1000 -c 10 https://gurukul-backend-kap2.onrender.com/health

# Test with 25 concurrent users
ab -n 2500 -c 25 https://gurukul-backend-kap2.onrender.com/health

# Test with 50 concurrent users
ab -n 5000 -c 50 https://gurukul-backend-kap2.onrender.com/health

# Test with 100 concurrent users
ab -n 10000 -c 100 https://gurukul-backend-kap2.onrender.com/health
```

### Expected Results

| Concurrent Users | Requests/sec | Avg Response Time | Error Rate | Status |
|-----------------|--------------|-------------------|------------|--------|
| 10 | 50-100 | <100ms | 0% | ✅ Expected |
| 25 | 40-80 | <200ms | 0% | ✅ Expected |
| 50 | 30-60 | <300ms | <1% | ⚠️ May degrade |
| 100 | 20-40 | <500ms | <5% | ⚠️ May degrade |

### Actual Results

**Status:** ⚠️ Not yet executed (simulated)

**Recommendation:** Run actual stress test in staging environment before production.

---

## Test 2: Auth Load

### Objective

Test authentication endpoints under load.

### Test Parameters

- **Concurrent Users:** 10, 25, 50
- **Duration:** 60 seconds per test
- **Endpoint:** `POST /api/v1/auth/login`
- **Payload:** Valid credentials (test account)

### Test Script

```bash
# Test login with 10 concurrent users
ab -n 500 -c 10 -p login.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/auth/login

# Test login with 25 concurrent users
ab -n 1250 -c 25 -p login.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/auth/login

# Test login with 50 concurrent users
ab -n 2500 -c 50 -p login.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/auth/login
```

**login.json:**
```json
{
  "email": "test@example.com",
  "password": "testpassword"
}
```

### Expected Results

| Concurrent Users | Requests/sec | Avg Response Time | Error Rate | Status |
|-----------------|--------------|-------------------|------------|--------|
| 10 | 20-40 | <200ms | 0% | ✅ Expected |
| 25 | 15-30 | <300ms | <1% | ✅ Expected |
| 50 | 10-20 | <500ms | <5% | ⚠️ May degrade |

### Degradation Behavior

- **Database Connection Pool:** Limited to 5 connections (may cause queuing)
- **JWT Generation:** Fast (python-jose)
- **Expected Bottleneck:** Database connection pool

### Actual Results

**Status:** ⚠️ Not yet executed (simulated)

**Recommendation:** Run actual stress test with real database.

---

## Test 3: Quiz Access

### Objective

Test quiz generation and submission under load.

### Test Parameters

- **Concurrent Users:** 5, 10, 25
- **Duration:** 60 seconds per test
- **Endpoints:** 
  - `POST /api/v1/quiz/generate`
  - `POST /api/v1/quiz/submit`

### Test Script

```bash
# Test quiz generation with 5 concurrent users
ab -n 100 -c 5 -p quiz_generate.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/quiz/generate

# Test quiz submission with 5 concurrent users
ab -n 100 -c 5 -p quiz_submit.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/quiz/submit
```

**quiz_generate.json:**
```json
{
  "subject": "Mathematics",
  "topic": "Algebra",
  "difficulty": "medium",
  "num_questions": 5
}
```

**quiz_submit.json:**
```json
{
  "quiz_id": "test_quiz_id",
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C"
  }
}
```

### Expected Results

| Concurrent Users | Requests/sec | Avg Response Time | Error Rate | Status |
|-----------------|--------------|-------------------|------------|--------|
| 5 | 5-10 | <2s | 0% | ✅ Expected |
| 10 | 3-8 | <3s | <1% | ✅ Expected |
| 25 | 2-5 | <5s | <5% | ⚠️ May degrade |

### Degradation Behavior

- **LLM API Calls:** Groq API has rate limits
- **Expected Bottleneck:** External API (Groq) rate limiting
- **Fallback:** Error message returned, no crash

### Actual Results

**Status:** ⚠️ Not yet executed (simulated)

**Recommendation:** Test with real Groq API key and monitor rate limits.

---

## Test 4: Chat Access

### Objective

Test chat endpoint under load.

### Test Parameters

- **Concurrent Users:** 5, 10, 25
- **Duration:** 60 seconds per test
- **Endpoint:** `POST /api/v1/chat/send`

### Test Script

```bash
# Test chat with 5 concurrent users
ab -n 100 -c 5 -p chat_message.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/chat/send

# Test chat with 10 concurrent users
ab -n 200 -c 10 -p chat_message.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/chat/send

# Test chat with 25 concurrent users
ab -n 500 -c 25 -p chat_message.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/chat/send
```

**chat_message.json:**
```json
{
  "message": "What is algebra?",
  "user_id": "test_user_123",
  "conversation_id": "test_conv_123"
}
```

### Expected Results

| Concurrent Users | Requests/sec | Avg Response Time | Error Rate | Status |
|-----------------|--------------|-------------------|------------|--------|
| 5 | 3-8 | <3s | 0% | ✅ Expected |
| 10 | 2-5 | <5s | <1% | ✅ Expected |
| 25 | 1-3 | <10s | <5% | ⚠️ May degrade |

### Degradation Behavior

- **LLM API Calls:** Groq API has rate limits
- **Expected Bottleneck:** External API (Groq) rate limiting
- **Fallback:** Error message returned, no crash

### Actual Results

**Status:** ⚠️ Not yet executed (simulated)

**Recommendation:** Test with real Groq API key and monitor rate limits.

---

## Test 5: Lesson Access

### Objective

Test lesson generation under load.

### Test Parameters

- **Concurrent Users:** 5, 10, 25
- **Duration:** 60 seconds per test
- **Endpoint:** `POST /api/v1/learning/explore`

### Test Script

```bash
# Test lesson generation with 5 concurrent users
ab -n 100 -c 5 -p lesson_request.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/learning/explore

# Test lesson generation with 10 concurrent users
ab -n 200 -c 10 -p lesson_request.json -T application/json \
  https://gurukul-backend-kap2.onrender.com/api/v1/learning/explore
```

**lesson_request.json:**
```json
{
  "subject": "Mathematics",
  "topic": "Algebra",
  "user_id": "test_user_123"
}
```

### Expected Results

| Concurrent Users | Requests/sec | Avg Response Time | Error Rate | Status |
|-----------------|--------------|-------------------|------------|--------|
| 5 | 3-8 | <3s | 0% | ✅ Expected |
| 10 | 2-5 | <5s | <1% | ✅ Expected |
| 25 | 1-3 | <10s | <5% | ⚠️ May degrade |

### Degradation Behavior

- **LLM API Calls:** Groq API has rate limits
- **Database Queries:** May be slow under load
- **Expected Bottleneck:** External API (Groq) rate limiting

### Actual Results

**Status:** ⚠️ Not yet executed (simulated)

**Recommendation:** Test with real Groq API key and monitor rate limits.

---

## Latency Analysis

### Baseline Latency (No Load)

| Endpoint | Avg Response Time | P95 Response Time | P99 Response Time |
|----------|-------------------|-------------------|-------------------|
| `/health` | <50ms | <100ms | <200ms |
| `/api/v1/auth/login` | <200ms | <300ms | <500ms |
| `/api/v1/quiz/generate` | <2s | <3s | <5s |
| `/api/v1/chat/send` | <2s | <3s | <5s |
| `/api/v1/learning/explore` | <2s | <3s | <5s |

### Latency Under Load (Expected)

| Endpoint | 10 Users | 25 Users | 50 Users |
|----------|----------|----------|----------|
| `/health` | <100ms | <200ms | <300ms |
| `/api/v1/auth/login` | <300ms | <500ms | <1s |
| `/api/v1/quiz/generate` | <3s | <5s | <10s |
| `/api/v1/chat/send` | <3s | <5s | <10s |
| `/api/v1/learning/explore` | <3s | <5s | <10s |

---

## Failure Analysis

### Failure Modes Observed (Expected)

1. **Database Connection Pool Exhausted**
   - **Symptom:** Slow responses, timeout errors
   - **Threshold:** >25 concurrent database requests
   - **Mitigation:** Increase connection pool size

2. **External API Rate Limiting**
   - **Symptom:** 429 Too Many Requests errors
   - **Threshold:** Groq API rate limits
   - **Mitigation:** Implement rate limiting, queue requests

3. **Memory Limit Exceeded**
   - **Symptom:** Service killed by OOM killer
   - **Threshold:** >512 MB memory usage
   - **Mitigation:** Optimize memory usage, remove heavy dependencies

4. **Cold Start Delays**
   - **Symptom:** First request slow (30-60s)
   - **Threshold:** After inactivity period
   - **Mitigation:** Keep-alive ping, pre-warm service

---

## Degradation Behavior

### Graceful Degradation

- **Database Failures:** Features return errors, server continues
- **External API Failures:** Features return errors, server continues
- **Router Failures:** Specific features unavailable, others work
- **Memory Pressure:** Service may slow down but continues

### Failure Recovery

- **Automatic:** Service restarts on crash (Render)
- **Manual:** Rollback deployment if needed
- **Monitoring:** Logs and metrics for failure detection

---

## Recommendations

### Before Production

1. **Run Actual Stress Tests:**
   - Execute stress tests in staging environment
   - Measure actual performance metrics
   - Identify real bottlenecks

2. **Set Up Monitoring:**
   - Monitor response times
   - Monitor error rates
   - Monitor resource usage (memory, CPU)

3. **Set Up Alerting:**
   - Alert on high error rates
   - Alert on slow response times
   - Alert on resource exhaustion

### Performance Optimizations

1. **Database Connection Pool:**
   - Increase pool size if needed
   - Implement connection pooling best practices

2. **External API Rate Limiting:**
   - Implement client-side rate limiting
   - Queue requests if rate limit exceeded
   - Cache responses when possible

3. **Memory Optimization:**
   - Monitor memory usage
   - Remove unused dependencies
   - Optimize data structures

---

## Stress Test Execution Plan

### Phase 1: Baseline (Completed)

- [x] Document stress test methodology
- [x] Identify test endpoints
- [x] Define test parameters

### Phase 2: Staging Tests (TODO)

- [ ] Set up staging environment
- [ ] Run concurrent user tests
- [ ] Run auth load tests
- [ ] Run quiz/chat/lesson tests
- [ ] Document actual results

### Phase 3: Production Tests (TODO)

- [ ] Run limited stress tests in production
- [ ] Monitor production metrics
- [ ] Document production behavior

---

## Conclusion

**Current Status:** ⚠️ Stress test methodology documented, actual tests pending

**Key Findings:**
- System designed for graceful degradation
- Expected bottlenecks: Database pool, external APIs
- Failure modes identified and documented

**Next Steps:**
- Execute actual stress tests in staging
- Measure real performance metrics
- Optimize based on results

---

## Appendix: Test Scripts

### Complete Stress Test Script

```bash
#!/bin/bash
# stress_test.sh - Run stress tests on Gurukul Backend

BASE_URL="https://gurukul-backend-kap2.onrender.com"

echo "Stress Test: Health Endpoint"
ab -n 1000 -c 10 ${BASE_URL}/health

echo "Stress Test: Auth Login"
ab -n 500 -c 10 -p login.json -T application/json \
  ${BASE_URL}/api/v1/auth/login

echo "Stress Test: Quiz Generation"
ab -n 100 -c 5 -p quiz_generate.json -T application/json \
  ${BASE_URL}/api/v1/quiz/generate

echo "Stress Test: Chat"
ab -n 100 -c 5 -p chat_message.json -T application/json \
  ${BASE_URL}/api/v1/chat/send

echo "Stress Test: Lesson Generation"
ab -n 100 -c 5 -p lesson_request.json -T application/json \
  ${BASE_URL}/api/v1/learning/explore
```

**Status:** Ready to execute (requires test data files)
