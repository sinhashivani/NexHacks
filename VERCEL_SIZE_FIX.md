# 🔧 Fixing "250 MB Size Limit Exceeded" Error

## Problem

Vercel has a **250 MB limit** for unzipped serverless functions. Your deployment is exceeding this limit.

## Root Causes

1. **Large Python dependencies** (scipy, numpy, pandas can be 50-100MB each)
2. **CSV/data files** being included in deployment
3. **Deploying from wrong directory** (backend/ instead of root)
4. **Unnecessary files** being bundled

## Solution 1: Use Root Directory (Recommended)

**You should deploy from the ROOT directory, not `backend/`:**

```bash
# Go to ROOT directory
cd c:\Users\shilo\NexHacks\NexHacks

# Deploy from root (uses api/ directory)
vercel --prod
```

The root `vercel.json` points to `api/index.py`, which is the correct setup.

---

## Solution 2: Create .vercelignore in Backend

If you must deploy from `backend/`, I've created `backend/.vercelignore` to exclude:
- CSV files
- Data directories
- Documentation
- Test files
- Build artifacts

---

## Solution 3: Reduce Dependencies

Check `backend/requirements.txt` for large packages:

**Large packages to consider:**
- `scipy` (~50MB) - Only needed if you're doing scientific computing
- `numpy` (~20MB) - Only needed for numerical operations
- `pandas` (~30MB) - Only needed for data analysis

**If not needed, remove them:**
```bash
# Edit backend/requirements.txt
# Remove: scipy, numpy, pandas (if not used)
```

---

## Solution 4: Check What's Being Deployed

```powershell
# See what files are being included
cd backend
Get-ChildItem -Recurse -File | 
  Where-Object { $_.Length -gt 1MB } | 
  Sort-Object Length -Descending | 
  Select-Object FullName, @{Name="MB";Expression={[math]::Round($_.Length/1MB,2)}} | 
  Format-Table -AutoSize
```

---

## Recommended Approach

**Deploy from ROOT, not backend:**

1. **Go to root directory:**
   ```bash
   cd c:\Users\shilo\NexHacks\NexHacks
   ```

2. **Verify vercel.json points to api/:**
   ```json
   {
     "routes": [
       {
         "src": "/(.*)",
         "dest": "api/index.py"
       }
     ]
   }
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

4. **The root `.vercelignore` already excludes:**
   - `backend/` directory ✅
   - CSV files ✅
   - Data files ✅
   - Documentation ✅

---

## Why Backend Directory is Too Large

The `backend/` directory might include:
- Large dependencies
- Test files
- Data files
- Documentation
- Duplicate code

**The `api/` directory is cleaner and designed for Vercel deployment.**

---

## Quick Fix

```bash
# 1. Go to root
cd c:\Users\shilo\NexHacks\NexHacks

# 2. Remove backend/.vercel if it exists (wrong project)
Remove-Item -Path "backend\.vercel" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Deploy from root
vercel --prod
```

---

## Verify Deployment Size

After deploying, check Vercel dashboard:
- Go to your project → Deployments
- Click on the deployment
- Check "Function Logs" → Look for size warnings

---

## If Still Too Large

1. **Check dependencies:**
   ```bash
   pip list --format=freeze | Select-String "scipy|numpy|pandas"
   ```

2. **Remove unused packages** from `api/requirements.txt`

3. **Use Vercel's dependency optimization:**
   - Vercel automatically optimizes some packages
   - But large scientific libraries can't be optimized much

4. **Consider splitting:**
   - Move heavy computation to a separate service
   - Use Vercel for lightweight API endpoints only

---

## Summary

**The issue:** Deploying from `backend/` which includes too many files.

**The fix:** Deploy from **root directory** which uses the cleaner `api/` setup.

```bash
cd c:\Users\shilo\NexHacks\NexHacks
vercel --prod
```

This will use `api/index.py` and respect the root `.vercelignore` file.
