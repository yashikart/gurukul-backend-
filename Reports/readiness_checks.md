# Readiness Checks

**Date:** February 14, 2026  
**System:** Gurukul Backend  
**Purpose:** Add clear health/readiness checks for deployment verification

---

## Health vs Readiness

### Health Check (`/health`)
- **Purpose:** Is the service alive and responding?
- **Use Case:** Load balancer, monitoring, basic status
- **Current Status:** ✅ Basic implementation exists

### Readiness Check (`/ready`)
- **Purpose:** Is the service ready to accept traffic?
- **Use Case:** Kubernetes readiness probe, deployment verification
- **Current Status:** ❌ Not implemented (TODO)

---

## Current Health Check Implementation

### Endpoint: `GET /health`

**Location:** `backend/app/main.py` lines 410-425

**Current Implementation:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

**Status:** ✅ Basic - returns 200 OK always

**Limitations:**
- Doesn't check database connectivity
- Doesn't check router status
- Doesn't check external API availability
- Always returns "healthy" even if components fail

---

## Proposed Health Check Enhancement

### Enhanced Health Check

**Endpoint:** `GET /health`

**Proposed Implementation:**
```python
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns 200 if service is alive, 503 if critical components failed.
    """
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check database connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["components"]["database"] = "healthy"
    except Exception as e:
        status["components"]["database"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"
    
    # Check critical routers
    status["components"]["auth_router"] = "healthy" if auth else "unhealthy"
    if not auth:
        status["status"] = "unhealthy"
    
    # Check external APIs (non-blocking)
    if settings.GROQ_API_KEY:
        status["components"]["groq_api"] = "configured"
    else:
        status["components"]["groq_api"] = "not_configured"
    
    # Determine HTTP status code
    if status["status"] == "unhealthy":
        return JSONResponse(status_code=503, content=status)
    elif status["status"] == "degraded":
        return JSONResponse(status_code=200, content=status)
    else:
        return status
```

**Status:** ⚠️ Proposed, not yet implemented

---

## Proposed Readiness Check

### Readiness Check Endpoint

**Endpoint:** `GET /ready`

**Purpose:** Verify service is ready to accept traffic

**Proposed Implementation:**
```python
@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    Returns 200 only if all critical components are ready.
    """
    checks = {
        "ready": True,
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check 1: Server is listening
    checks["checks"]["server"] = "ready"
    
    # Check 2: Auth router is loaded (critical)
    if auth:
        checks["checks"]["auth_router"] = "ready"
    else:
        checks["checks"]["auth_router"] = "not_ready"
        checks["ready"] = False
    
    # Check 3: Database is reachable (critical)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["checks"]["database"] = "ready"
    except Exception as e:
        checks["checks"]["database"] = f"not_ready: {str(e)}"
        checks["ready"] = False
    
    # Check 4: Core routers are loaded (non-critical but preferred)
    if chat and quiz and learning:
        checks["checks"]["core_routers"] = "ready"
    else:
        checks["checks"]["core_routers"] = "partial"
        # Don't fail readiness for this
    
    if checks["ready"]:
        return checks
    else:
        return JSONResponse(status_code=503, content=checks)
```

**Status:** ❌ Not implemented (TODO)

---

## Component-Specific Checks

### Database Readiness Check

**Check:** Database connection and basic query

**Implementation:**
```python
async def check_database_ready():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True, "ready"
    except Exception as e:
        return False, f"not_ready: {str(e)}"
```

**Timeout:** 5 seconds  
**Failure Impact:** Service degraded (non-blocking)

---

### Router Readiness Check

**Check:** Critical routers are imported and registered

**Implementation:**
```python
async def check_routers_ready():
    checks = {}
    
    # Auth router (critical)
    checks["auth"] = "ready" if auth else "not_ready"
    
    # Core routers (preferred)
    checks["chat"] = "ready" if chat else "not_ready"
    checks["quiz"] = "ready" if quiz else "not_ready"
    checks["learning"] = "ready" if learning else "not_ready"
    
    return checks
```

**Timeout:** N/A (check is instant)  
**Failure Impact:** 
- Auth router: Service unhealthy
- Other routers: Service degraded

---

### External API Readiness Check

**Check:** External API keys configured (non-blocking)

**Implementation:**
```python
async def check_external_apis_ready():
    checks = {}
    
    checks["groq"] = "configured" if settings.GROQ_API_KEY else "not_configured"
    checks["gemini"] = "configured" if settings.GEMINI_API_KEY else "not_configured"
    
    return checks
```

**Timeout:** N/A (check is instant)  
**Failure Impact:** Features unavailable (non-blocking)

---

## Readiness Check Matrix

| Component | Critical? | Blocks Readiness? | Check Method |
|-----------|-----------|-------------------|--------------|
| Server Listening | ✅ Yes | ✅ Yes | Port binding |
| Auth Router | ✅ Yes | ✅ Yes | Router import check |
| Database | ✅ Yes | ✅ Yes | Connection + query |
| Chat Router | ❌ No | ❌ No | Router import check |
| Quiz Router | ❌ No | ❌ No | Router import check |
| Learning Router | ❌ No | ❌ No | Router import check |
| Groq API Key | ❌ No | ❌ No | Env var check |
| Gemini API Key | ❌ No | ❌ No | Env var check |
| PRANA | ❌ No | ❌ No | N/A (non-blocking) |

---

## Deployment Readiness Checklist

### Pre-Deployment Checks

- [ ] Code changes reviewed and tested
- [ ] Environment variables verified in Render dashboard
- [ ] Database migrations tested (if any)
- [ ] Dependencies updated (if any)

### Post-Deployment Checks

- [ ] Health endpoint returns 200: `curl /health`
- [ ] Readiness endpoint returns 200: `curl /ready` (when implemented)
- [ ] Database connectivity verified
- [ ] Auth endpoint responds: `curl /api/v1/auth/login`
- [ ] Critical features tested (login, chat, quiz)

---

## Health Check Response Examples

### Healthy Service

```json
{
  "status": "healthy",
  "timestamp": "2026-02-14T10:30:00",
  "components": {
    "database": "healthy",
    "auth_router": "healthy",
    "core_routers": "healthy",
    "groq_api": "configured"
  }
}
```

**HTTP Status:** 200 OK

---

### Degraded Service

```json
{
  "status": "degraded",
  "timestamp": "2026-02-14T10:30:00",
  "components": {
    "database": "healthy",
    "auth_router": "healthy",
    "core_routers": "partial",
    "groq_api": "not_configured"
  }
}
```

**HTTP Status:** 200 OK (service works but some features unavailable)

---

### Unhealthy Service

```json
{
  "status": "unhealthy",
  "timestamp": "2026-02-14T10:30:00",
  "components": {
    "database": "unhealthy: connection timeout",
    "auth_router": "healthy",
    "core_routers": "healthy",
    "groq_api": "configured"
  }
}
```

**HTTP Status:** 503 Service Unavailable

---

## Readiness Check Response Examples

### Ready Service

```json
{
  "ready": true,
  "timestamp": "2026-02-14T10:30:00",
  "checks": {
    "server": "ready",
    "auth_router": "ready",
    "database": "ready",
    "core_routers": "ready"
  }
}
```

**HTTP Status:** 200 OK

---

### Not Ready Service

```json
{
  "ready": false,
  "timestamp": "2026-02-14T10:30:00",
  "checks": {
    "server": "ready",
    "auth_router": "not_ready",
    "database": "ready",
    "core_routers": "partial"
  }
}
```

**HTTP Status:** 503 Service Unavailable

---

## Integration with DevOps Platform

### Render.com Configuration

**Health Check Path:** `/health`  
**Health Check Interval:** 30 seconds (Render default)  
**Health Check Timeout:** 10 seconds (Render default)

**Current Status:** ✅ Configured (basic health check)

**Recommended Enhancement:**
- Add readiness check path: `/ready`
- Configure readiness check in Render (if supported)

---

### Kubernetes (Future)

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Status:** ❌ Not applicable (using Render, not Kubernetes)

---

## Monitoring and Alerting

### Health Check Monitoring

**Current Status:** ⚠️ Manual checks only

**Recommended:**
1. Set up automated health check monitoring
2. Alert on health check failures
3. Dashboard for health check status
4. Historical health check data

---

### Readiness Check Monitoring

**Current Status:** ❌ Not implemented

**Recommended:**
1. Monitor readiness check endpoint
2. Alert on readiness failures
3. Track readiness metrics
4. Correlate readiness with deployment success

---

## Testing Readiness Checks

### Test Health Check

```bash
# Test health endpoint
curl https://gurukul-backend-kap2.onrender.com/health

# Expected: 200 OK with {"status": "healthy", ...}
```

### Test Readiness Check (when implemented)

```bash
# Test readiness endpoint
curl https://gurukul-backend-kap2.onrender.com/ready

# Expected: 200 OK if ready, 503 if not ready
```

### Test Failure Scenarios

```bash
# Simulate database failure (remove DATABASE_URL temporarily)
# Health check should return degraded/unhealthy

# Simulate router failure (comment out router import)
# Readiness check should return not_ready
```

---

## Implementation Checklist

### ✅ Current Implementation

- [x] Basic health check endpoint (`/health`)
- [x] Returns 200 OK always
- [x] Includes timestamp

### ⚠️ Proposed Enhancements

- [ ] Enhanced health check with component status
- [ ] Readiness check endpoint (`/ready`)
- [ ] Database connectivity check
- [ ] Router status check
- [ ] External API status check
- [ ] HTTP status codes based on health state

### ❌ Future Enhancements

- [ ] Health check metrics/logging
- [ ] Health check dashboard
- [ ] Automated health check monitoring
- [ ] Health check alerting
- [ ] Historical health check data

---

## Recommendations

### Immediate (Before Demo)

1. ✅ **Already Done:** Basic health check exists
2. ⚠️ **Enhance:** Add database check to health endpoint
3. ⚠️ **Add:** Readiness check endpoint (`/ready`)
4. ⚠️ **Add:** Router status to health check

### Short-Term (Post-Demo)

1. Implement comprehensive health check with all components
2. Add health check metrics/logging
3. Set up automated health check monitoring
4. Add health check alerting

### Long-Term (Future)

1. Health check dashboard
2. Historical health check data
3. Predictive health check analysis
4. Automated recovery based on health checks

---

## Conclusion

**Current Status:** ✅ Basic health check implemented

**Key Achievements:**
- Health endpoint exists and responds
- Returns basic status information

**Next Steps:**
- Enhance health check with component status
- Add readiness check endpoint
- Add component-specific checks
- Integrate with monitoring/alerting
