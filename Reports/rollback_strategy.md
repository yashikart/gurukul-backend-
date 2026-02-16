# Rollback Strategy

**Date:** February 14, 2026  
**System:** Gurukul Backend  
**Purpose:** Define deterministic rollback steps - what gets reverted, what stays untouched, how to recover within minutes

---

## Rollback Philosophy

1. **Deterministic:** Same steps work every time
2. **Fast:** Recovery within minutes, not hours
3. **Safe:** No data loss, no service disruption beyond rollback window
4. **Documented:** Clear steps for anyone to execute

---

## Rollback Scenarios

### Scenario 1: Code Deployment Failure

**Trigger:** New deployment causes errors, crashes, or critical bugs  
**Recovery Time Target:** <5 minutes  
**Data Impact:** None (code rollback only)

---

### Scenario 2: Configuration Change Failure

**Trigger:** Environment variable change causes service failure  
**Recovery Time Target:** <2 minutes  
**Data Impact:** None (config rollback only)

---

### Scenario 3: Database Migration Failure

**Trigger:** Schema change breaks application  
**Recovery Time Target:** <10 minutes  
**Data Impact:** Potential (if migration partially applied)

---

### Scenario 4: Dependency Update Failure

**Trigger:** New package version causes incompatibility  
**Recovery Time Target:** <5 minutes  
**Data Impact:** None (dependency rollback only)

---

## Rollback Methods

### Method 1: Git Revert (Recommended for Code Changes)

**Use Case:** Code deployment failure  
**Time:** <5 minutes  
**Steps:**

```bash
# 1. Identify the problematic commit
git log --oneline -10

# 2. Revert the commit (creates new commit that undoes changes)
git revert <commit-hash>

# 3. Push to trigger new deployment
git push origin main

# 4. Monitor deployment in Render dashboard
# 5. Verify service is working
curl https://gurukul-backend-kap2.onrender.com/health
```

**What Gets Reverted:**
- ✅ Code changes
- ✅ File modifications
- ❌ Environment variables (unchanged)
- ❌ Database schema (unchanged)

**What Stays Untouched:**
- Environment variables in Render dashboard
- Database data and schema
- External service configurations

---

### Method 2: Render Dashboard Rollback (Fastest)

**Use Case:** Any deployment failure  
**Time:** <2 minutes  
**Steps:**

1. **Open Render Dashboard**
   - Navigate to: https://dashboard.render.com
   - Select: Gurukul Backend service

2. **Find Previous Deployment**
   - Go to "Deploys" tab
   - Find last known working deployment (green status)
   - Note the commit hash and timestamp

3. **Redeploy Previous Version**
   - Click on the working deployment
   - Click "Redeploy" button
   - Confirm redeployment

4. **Monitor Rollback**
   - Watch deployment logs
   - Verify service starts successfully
   - Check health endpoint

5. **Verify Service**
   ```bash
   curl https://gurukul-backend-kap2.onrender.com/health
   # Expected: {"status": "healthy"}
   ```

**What Gets Reverted:**
- ✅ Code to previous version
- ✅ Dependencies to previous versions
- ❌ Environment variables (unchanged)
- ❌ Database schema (unchanged)

**What Stays Untouched:**
- Environment variables
- Database data and schema
- External service configurations

---

### Method 3: Environment Variable Rollback

**Use Case:** Configuration change failure  
**Time:** <2 minutes  
**Steps:**

1. **Identify Problem Variable**
   - Check Render logs for configuration errors
   - Identify which env var caused the issue

2. **Revert in Render Dashboard**
   - Go to: Render Dashboard → Service → Environment
   - Find the problematic variable
   - Change back to previous value OR remove if not required
   - Save changes

3. **Restart Service**
   - Render automatically restarts on env var change
   - OR manually restart: Service → Manual Deploy → Restart

4. **Verify Service**
   ```bash
   curl https://gurukul-backend-kap2.onrender.com/health
   ```

**What Gets Reverted:**
- ✅ Environment variable value
- ❌ Code (unchanged)
- ❌ Database (unchanged)

**What Stays Untouched:**
- Code
- Database
- Other environment variables

---

### Method 4: Database Migration Rollback

**Use Case:** Schema change breaks application  
**Time:** <10 minutes  
**Steps:**

**⚠️ WARNING:** Database rollback may cause data loss if migration partially applied.

1. **Stop Service** (if needed)
   - Render Dashboard → Service → Manual Deploy → Stop

2. **Connect to Database**
   ```bash
   # Get connection string from Render dashboard
   psql $DATABASE_URL
   ```

3. **Check Migration Status**
   ```sql
   -- Check if alembic_version table exists
   SELECT * FROM alembic_version;
   
   -- Or check schema changes manually
   \dt  -- List tables
   ```

4. **Rollback Migration**
   ```bash
   # If using Alembic
   alembic downgrade -1  # Rollback one version
   
   # OR manual SQL rollback
   psql $DATABASE_URL -f rollback_migration.sql
   ```

5. **Restart Service**
   - Render Dashboard → Service → Manual Deploy → Restart

6. **Verify Service**
   ```bash
   curl https://gurukul-backend-kap2.onrender.com/health
   ```

**What Gets Reverted:**
- ✅ Database schema
- ❌ Code (may need code rollback too)
- ❌ Environment variables (unchanged)

**What Stays Untouched:**
- Environment variables
- Other database data (if rollback is clean)

---

## Rollback Decision Tree

```
Deployment Failure Detected
│
├─ Is it a code issue?
│  ├─ YES → Use Method 1 (Git Revert) OR Method 2 (Render Dashboard)
│  └─ NO → Continue
│
├─ Is it a configuration issue?
│  ├─ YES → Use Method 3 (Environment Variable Rollback)
│  └─ NO → Continue
│
├─ Is it a database issue?
│  ├─ YES → Use Method 4 (Database Migration Rollback)
│  └─ NO → Continue
│
└─ Unknown → Use Method 2 (Render Dashboard - safest)
```

---

## Rollback Checklist

### Pre-Rollback

- [ ] Identify the failure (check logs, error messages)
- [ ] Determine rollback method (code/config/database)
- [ ] Identify last known working state (commit hash, timestamp)
- [ ] Notify team (if during business hours)
- [ ] Backup database (if database rollback needed)

### During Rollback

- [ ] Execute rollback steps (see methods above)
- [ ] Monitor deployment logs
- [ ] Watch for errors during rollback
- [ ] Verify service starts successfully

### Post-Rollback

- [ ] Verify health endpoint responds
- [ ] Test critical features (login, chat, quiz)
- [ ] Check application logs for errors
- [ ] Document what was rolled back and why
- [ ] Create issue/ticket for root cause analysis

---

## Rollback Time Estimates

| Method | Time | Complexity | Risk |
|--------|------|------------|------|
| Git Revert | 5 min | Medium | Low |
| Render Dashboard | 2 min | Low | Low |
| Env Var Rollback | 2 min | Low | Low |
| DB Migration | 10 min | High | Medium |

**Note:** Times assume you have access to Render dashboard and git repository.

---

## What Gets Reverted vs What Stays Untouched

### Code Rollback (Method 1 or 2)

**Gets Reverted:**
- ✅ Application code
- ✅ Dependencies (if requirements.txt changed)
- ✅ Configuration files in repo

**Stays Untouched:**
- ❌ Environment variables in Render dashboard
- ❌ Database data and schema
- ❌ External service configurations
- ❌ Render service settings

---

### Configuration Rollback (Method 3)

**Gets Reverted:**
- ✅ Environment variable values
- ✅ Render service settings (if changed)

**Stays Untouched:**
- ❌ Application code
- ❌ Database
- ❌ Other environment variables

---

### Database Rollback (Method 4)

**Gets Reverted:**
- ✅ Database schema changes
- ✅ Migration history (if using Alembic)

**Stays Untouched:**
- ❌ Application code (may need separate rollback)
- ❌ Environment variables
- ❌ Other database data (if rollback is clean)

---

## Recovery Procedures

### Recovery After Code Rollback

1. **Verify Service**
   ```bash
   curl https://gurukul-backend-kap2.onrender.com/health
   ```

2. **Test Critical Features**
   ```bash
   # Test login
   curl -X POST https://gurukul-backend-kap2.onrender.com/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test"}'
   
   # Test health
   curl https://gurukul-backend-kap2.onrender.com/health
   ```

3. **Check Logs**
   - Render Dashboard → Service → Logs
   - Look for errors or warnings

4. **Monitor for 15 minutes**
   - Watch for any recurring errors
   - Check error rates

---

### Recovery After Configuration Rollback

1. **Verify Service Restarted**
   - Check Render logs for restart confirmation

2. **Test Configuration**
   ```bash
   # Test endpoints that use the reverted config
   curl https://gurukul-backend-kap2.onrender.com/health
   ```

3. **Verify No Errors**
   - Check logs for configuration-related errors

---

### Recovery After Database Rollback

1. **Verify Database Schema**
   ```sql
   -- Connect to database
   psql $DATABASE_URL
   
   -- Check tables exist
   \dt
   
   -- Verify critical tables
   SELECT COUNT(*) FROM users;
   ```

2. **Test Database-Dependent Features**
   ```bash
   # Test login (uses database)
   curl -X POST https://gurukul-backend-kap2.onrender.com/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test"}'
   ```

3. **Check for Data Loss**
   - Verify critical data still exists
   - Check if any data was lost during rollback

---

## Emergency Contacts

| Issue | Contact | Method |
|-------|---------|--------|
| Code Rollback | Yashika | Git/Render Dashboard |
| Config Rollback | Yashika | Render Dashboard |
| Database Rollback | Yashika | Database Access Required |
| Render Platform Issue | Render Support | support@render.com |

---

## Rollback Testing

### Test Rollback Procedure (Quarterly)

1. **Create Test Branch**
   ```bash
   git checkout -b test-rollback
   ```

2. **Make Test Change**
   - Add a comment to `main.py`
   - Commit and push

3. **Deploy Test Change**
   - Merge to main (or deploy test branch)
   - Verify deployment

4. **Execute Rollback**
   - Use Method 2 (Render Dashboard)
   - Rollback to previous deployment

5. **Verify Rollback**
   - Check service is working
   - Verify change is reverted

6. **Cleanup**
   - Delete test branch
   - Document test results

---

## Rollback Documentation Template

```markdown
# Rollback Report

**Date:** [Date]
**Time:** [Time]
**Rollback Method:** [Method 1/2/3/4]
**Trigger:** [What caused the rollback]
**Previous State:** [Commit hash, timestamp]
**Rollback To:** [Commit hash, timestamp]
**Duration:** [Time taken]
**Result:** [Success/Failure]
**Root Cause:** [Why rollback was needed]
**Prevention:** [How to prevent in future]
```

---

## Prevention Strategies

### Before Deployment

1. **Code Review:** All changes reviewed before merge
2. **Testing:** Test changes locally before deploying
3. **Staging:** Deploy to staging environment first (if available)
4. **Backup:** Backup database before major changes

### During Deployment

1. **Monitor:** Watch deployment logs in real-time
2. **Health Check:** Verify health endpoint immediately after deploy
3. **Smoke Test:** Test critical features after deploy

### After Deployment

1. **Monitor:** Watch logs and metrics for 15-30 minutes
2. **Alert:** Set up alerts for errors and failures
3. **Document:** Document any issues or concerns

---

## Conclusion

**Rollback Capability:** ✅ Fully supported via multiple methods

**Recovery Time:** <10 minutes for all scenarios

**Risk Level:** Low (deterministic steps, no data loss for code/config rollbacks)

**Next Steps:**
- Test rollback procedure quarterly
- Document rollback incidents
- Improve prevention strategies based on rollback frequency
