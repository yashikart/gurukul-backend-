# Deployment Failure Analysis

## Root Causes

### BUILD FAILURES
| Cause                          | Fix                                         |
|--------------------------------|---------------------------------------------|
| PyTorch (~2GB) exceeds memory  | Remove `torch>=2.0.0` from requirements.txt |
| Transformers (~500MB)          | Remove `transformers>=4.30.0`               |
| Pip timeout on large downloads | Use `--no-cache-dir` flag                   |

### STARTUP FAILURES
| Cause                            | Fix                                      |
|----------------------------------|------------------------------------------|
| Heavy imports block port binding | Already fixed: deferred to startup event |
| LED model loads ~300MB           | Already fixed: summarizer disabled       |
| Missing DATABASE_URL             | Set in Render dashboard                  |

### ENV FAILURES
| Variable       | Action                                              |
|----------------|-----------------------------------------------------|
| `DATABASE_URL` | MUST set manually in Render                         |
| `SECRET_KEY`   | Auto-generated, verify exists                       |
| `FRONTEND_URL` | Set to `https://gurukul-frontend-738j.onrender.com` |

## Gurukul vs EMS
| Metric     | Gurukul    | EMS       | Action                               |
|------------|------------|-----------|--------------------------------------|
| Packages   | 57         | 17        | Remove unused ML packages            |
| Build time | 40-50 min  | 5-10 min  | Split heavy deps to separate service |
| Memory     | 400-600 MB | 80-150 MB | Upgrade Render plan or remove ML     |

## Immediate Actions

1. **Verify DATABASE_URL** → Render Dashboard → Environment
2. **Confirm summarizer disabled** → `backend/app/main.py` line 163-164
3. **Check CORS origins** → Must include production frontend URL

