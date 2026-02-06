# Render Deployment Fix

## Issue Summary
Render deployment was failing with:
- **Python version mismatch**: Render used 3.13.4 instead of specified 3.10.13
- **Missing dependency**: gunicorn not in requirements.txt
- **Build error**: `BackendUnavailable: Cannot import 'setuptools.build_meta'`

## Root Causes

### 1. Malformed `runtime.txt`
**Problem:** Extra line with `.` after python version
```
python-3.10.13
.                 ❌ Extra line caused file to be ignored
```

**Fixed:** Single line only
```
python-3.10.13    ✅ Correct format
```

### 2. Missing `gunicorn`
**Problem:** `render.yaml` uses gunicorn but it's not in `requirements.txt`
```yaml
startCommand: gunicorn api.agent_api:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Fixed:** Added to `requirements.txt`
```
gunicorn==21.2.0
```

## Changes Made

### 1. Fixed `runtime.txt`
```diff
- python-3.10.13
- .
+ python-3.10.13
```

### 2. Updated `requirements.txt`
```diff
  PyJWT==2.8.0
  uvicorn==0.24.0
  fastapi==0.104.1
+ gunicorn==21.2.0
```

## Deployment Steps

### 1. Commit and Push
```bash
git add runtime.txt requirements.txt
git commit -m "Fix Render deployment: runtime.txt format and add gunicorn"
git push origin main
```

### 2. Render Auto-Deploy
Render will automatically detect the push and redeploy.

### 3. Monitor Build
Watch the build output for:
- ✅ `Using Python version 3.10.13` (not 3.13.4)
- ✅ `Successfully installed gunicorn-21.2.0`
- ✅ `Build succeeded`

## Expected Build Output

```
==> Using Python version 3.10.13 (from runtime.txt)  ✅
==> Running build command 'pip install -r requirements.txt'...
==> Installing packages...
    ✅ pandas-2.0.3
    ✅ numpy-1.24.3
    ✅ fastapi-0.104.1
    ✅ uvicorn-0.24.0
    ✅ gunicorn-21.2.0
==> Build succeeded ✅
==> Starting service...
```

## Why This Works

1. **Correct Python Version**: runtime.txt now properly specifies Python 3.10.13
2. **All Dependencies**: gunicorn is now included for production server
3. **Package Compatibility**: numpy 1.24.3 and pandas 2.0.3 work with Python 3.10

## Verification

After deployment succeeds:

```bash
# Test health endpoint
curl https://your-app.onrender.com/api/agent/status

# Expected response:
{
  "agent_id": "agent-...",
  "state": "idle",
  "uptime_seconds": ...
}
```

## Files Changed

| File | Change | Purpose |
|------|--------|---------|
| `runtime.txt` | Removed extra line | Fix Python version detection |
| `requirements.txt` | Added gunicorn==21.2.0 | Add production server |

## Status
✅ **Ready to deploy** - Push changes and Render will auto-deploy
