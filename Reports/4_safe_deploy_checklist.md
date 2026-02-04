# Safe Deploy Checklist

## PRE-DEPLOY

```
[ ] DATABASE_URL set in Render dashboard
[ ] SECRET_KEY exists (auto-generated OK)
[ ] FRONTEND_URL = https://gurukul-frontend-738j.onrender.com
[ ] Summarizer import commented out (main.py line 163-164)
[ ] No localhost URLs in production code
```

## DEPLOY

```
[ ] Trigger deploy (push to main OR manual in Render)
[ ] Watch build logs for "Successfully installed"
[ ] Watch startup logs for "[Startup] ✓ Auth router"
[ ] Wait for "Uvicorn running on..."
```

## POST-DEPLOY

```bash
# Test health
curl https://gurukul-up9j.onrender.com/health
# Expected: {"status":"healthy"}

# Test auth
curl https://gurukul-up9j.onrender.com/api/v1/auth/me
# Expected: 401 Unauthorized (working correctly)

# Test docs
# Open: https://gurukul-up9j.onrender.com/docs
```

## FRONTEND TEST

```
[ ] Open https://gurukul-frontend-738j.onrender.com
[ ] Login with test account
[ ] Check browser console (ignore PRANA errors)
[ ] Try Chat feature
[ ] Try Quiz feature
```

## ROLLBACK

```bash
# Option 1: Revert code
git revert HEAD && git push origin main

# Option 2: Render dashboard
# → Deploys tab → Find last working → Redeploy
```

## QUICK FIXES

| Issue              | Fix                                                |
|--------------------|----------------------------------------------------|
| Build OOM          | Comment out torch/transformers in requirements.txt |
| Startup timeout    | Check main.py for blocking imports                 |
| DB connection fail | Verify DATABASE_URL format                         |
| 404 on PRANA       | Check bucket router registration                   |
| CORS errors        | Add frontend URL to allowed_origins                |

