# 🔍 Debugging 500 Internal Server Error

## Current Status

All endpoints are returning **500 Internal Server Error**. This indicates a server-side issue.

## Most Likely Causes

### 1. Missing Environment Variables (Most Common)

**Check Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select your project: **nexhacks**
3. Go to **Settings** → **Environment Variables**
4. Verify these are set for **Production**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `GEMINI_API_KEY` (optional)

**If missing, add them:**
- Click "Add New"
- Name: `SUPABASE_URL`
- Value: Your Supabase project URL
- Environments: Check **Production**, **Preview**, **Development**
- Click "Save"

Repeat for `SUPABASE_ANON_KEY` and `GEMINI_API_KEY`.

---

### 2. Check Vercel Logs

**Via CLI:**
```powershell
vercel logs https://nexhacks-nu.vercel.app --follow
```

**Via Dashboard:**
1. Go to Vercel Dashboard → Your Project
2. Click **Deployments** tab
3. Click on the latest deployment
4. Click **"Function Logs"** tab
5. Look for Python errors or import errors

**Common errors you might see:**
- `ValueError: Missing Supabase credentials` → Environment variables not set
- `ImportError: cannot import name 'X'` → Missing dependency or import issue
- `ModuleNotFoundError: No module named 'X'` → Missing package in requirements.txt

---

### 3. Verify Environment Variables Are Correct

**Test locally first:**
```powershell
# Create a test script
@"
import os
from dotenv import load_dotenv
load_dotenv()

print('SUPABASE_URL:', os.getenv('SUPABASE_URL')[:30] + '...' if os.getenv('SUPABASE_URL') else 'NOT SET')
print('SUPABASE_ANON_KEY:', os.getenv('SUPABASE_ANON_KEY')[:30] + '...' if os.getenv('SUPABASE_ANON_KEY') else 'NOT SET')
"@ | Out-File -FilePath test_env.py -Encoding utf8

python test_env.py
```

**Expected:** Both should show values (not "NOT SET")

---

### 4. Check Import Errors

**Test if the app can import:**
```powershell
python -c "from api.index import app; print('✅ Import successful')"
```

**If this fails locally:**
- Check `api/index.py` imports
- Check `api/main.py` imports
- Verify all dependencies in `api/requirements.txt`

---

## Quick Fix Steps

### Step 1: Add Environment Variables in Vercel

1. **Get your Supabase credentials:**
   - Go to Supabase Dashboard → Settings → API
   - Copy **Project URL** → Use as `SUPABASE_URL`
   - Copy **anon public key** → Use as `SUPABASE_ANON_KEY`

2. **Add to Vercel:**
   - Vercel Dashboard → Project → Settings → Environment Variables
   - Add each variable
   - **Important:** Select **Production** environment
   - Save

3. **Redeploy:**
   ```powershell
   vercel --prod
   ```

---

### Step 2: Check Logs After Redeploy

```powershell
# Wait 30 seconds for deployment, then:
vercel logs https://nexhacks-nu.vercel.app --follow
```

Look for:
- ✅ `Application startup complete` = Success
- ❌ `ValueError: Missing Supabase credentials` = Env vars not set
- ❌ `ImportError` = Import issue
- ❌ `ModuleNotFoundError` = Missing dependency

---

### Step 3: Test Again

```powershell
.\TEST_VERCEL_DEPLOYMENT.ps1
```

---

## Common Error Messages & Fixes

### Error: "Missing Supabase credentials"

**Fix:** Add `SUPABASE_URL` and `SUPABASE_ANON_KEY` to Vercel environment variables

---

### Error: "Cannot import 'X'"

**Fix:** 
1. Check if `X` is in `api/requirements.txt`
2. If missing, add it
3. Redeploy

---

### Error: "ModuleNotFoundError: No module named 'X'"

**Fix:**
1. Add `X` to `api/requirements.txt`
2. Redeploy

---

### Error: "Function timeout"

**Fix:**
1. Check if database queries are slow
2. Add indexes to database
3. Optimize queries

---

## Manual Test After Fixes

```powershell
# Test root endpoint
try {
    $result = Invoke-RestMethod -Uri "https://nexhacks-nu.vercel.app/"
    Write-Host "✅ Success!" -ForegroundColor Green
    $result | ConvertTo-Json
} catch {
    Write-Host "❌ Still failing:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
```

---

## Next Steps

1. ✅ **Add environment variables** in Vercel dashboard
2. ✅ **Redeploy** after adding variables
3. ✅ **Check logs** to see if errors are resolved
4. ✅ **Run test script again**

---

## Getting Help

If still failing after adding environment variables:

1. **Share the error logs:**
   ```powershell
   vercel logs https://nexhacks-nu.vercel.app --follow=false > logs.txt
   ```

2. **Check:**
   - Are environment variables set correctly?
   - Are they set for Production environment?
   - Do the values match your `.env` file locally?

3. **Test locally first:**
   - If it works locally but not on Vercel = Environment variable issue
   - If it fails locally = Code/import issue

---

The most common cause is **missing environment variables**. Add them in Vercel dashboard and redeploy! 🚀
