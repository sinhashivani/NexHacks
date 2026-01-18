# 🧪 Complete Vercel Deployment Testing Guide

## Quick Start

Run the automated test script:

```powershell
cd c:\Users\shilo\NexHacks\NexHacks
.\TEST_VERCEL_DEPLOYMENT.ps1
```

Or test a specific URL:

```powershell
.\TEST_VERCEL_DEPLOYMENT.ps1 -ApiUrl "https://your-url.vercel.app"
```

---

## Manual Testing Steps

### Step 1: Basic Connectivity (No Database Required)

#### Test Root Endpoint

```powershell
Invoke-RestMethod -Uri "https://nexhacks-nu.vercel.app/"
```

**Expected Response:**
```json
{
  "name": "NexHacks Polymarket API",
  "version": "1.0.0",
  "endpoints": {
    "trending": "/markets/trending",
    "ui": "/ui"
  }
}
```

**✅ Success:** Returns API info  
**❌ Failure:** 500 error = Check environment variables or deployment logs

---

#### Test CORS Endpoint

```powershell
Invoke-RestMethod -Uri "https://nexhacks-nu.vercel.app/test-cors"
```

**Expected Response:**
```json
{
  "status": "ok",
  "cors": "enabled",
  "message": "CORS test successful"
}
```

**✅ Success:** Returns CORS confirmation  
**❌ Failure:** 500 error = Check app initialization

---

#### Test Favicon Handler

```powershell
Invoke-WebRequest -Uri "https://nexhacks-nu.vercel.app/favicon.ico" -Method HEAD
```

**Expected:** Status Code 204 (No Content)  
**✅ Success:** No more 404 errors in logs  
**❌ Failure:** 404 = Favicon handler not working

---

### Step 2: Database Connectivity Tests

#### Test Trending Markets

```powershell
Invoke-RestMethod -Uri "https://nexhacks-nu.vercel.app/markets/trending?limit=5"
```

**Expected Response:**
```json
{
  "count": 5,
  "markets": [
    {
      "question": "...",
      "slug": "...",
      "last_price": 0.5,
      ...
    }
  ]
}
```

**✅ Success:** Returns array of markets  
**❌ Failure:** 
- `500 Internal Server Error` = Database connection issue
- Check `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Vercel dashboard
- Verify environment variables are set in **Production** environment

---

#### Test Similar Markets

```powershell
$title = [System.Uri]::EscapeDataString("Who will Trump nominate as Fed Chair?")
Invoke-RestMethod -Uri "https://nexhacks-nu.vercel.app/similar?event_title=$title&limit=5"
```

**Expected Response:**
```json
{
  "event_title": "Who will Trump nominate as Fed Chair?",
  "similar_markets": [...],
  "count": 5
}
```

**✅ Success:** Returns similar markets  
**❌ Failure:** 500 error = Database or similarity_scores table issue

---

#### Test Related Markets

```powershell
Invoke-RestMethod -Uri "https://nexhacks-nu.vercel.app/related?limit=5"
```

**✅ Success:** Returns related markets  
**❌ Failure:** 500 error = Database issue

---

### Step 3: Browser CORS Test (Critical!)

This is the **most important test** for extension integration.

1. **Open any website** (e.g., `https://polymarket.com`)
2. **Open DevTools** (F12) → **Console** tab
3. **Run this:**

```javascript
fetch('https://nexhacks-nu.vercel.app/markets/trending?limit=5')
  .then(r => r.json())
  .then(data => {
    console.log('✅ API Working:', data);
    console.log('✅ Count:', data.count);
  })
  .catch(err => {
    console.error('❌ Error:', err);
  })
```

**✅ Success:** 
- Data logged to console
- No CORS errors
- Returns market data

**❌ Failure:**
- `CORS policy` error = CORS middleware issue
- `Failed to fetch` = Network/URL issue
- `500` error = Backend issue
- `401` error = Deployment protection (use production URL)

---

### Step 4: Extension Integration Test

#### Update Extension (if needed)

```powershell
cd Extension

# Check current URL
Get-Content .env.production

# Update if needed
Set-Content -Path ".env.production" -Value "VITE_BACKEND=https://nexhacks-nu.vercel.app"

# Rebuild
npm run build:prod
```

#### Reload Extension

1. Go to `chrome://extensions`
2. Find "Polymarket Trade Assistant"
3. Click **Reload** button (🔄)

#### Test on Polymarket

1. Visit any Polymarket market page:
   - `https://polymarket.com/event/who-will-trump-nominate-as-fed-chair`
2. **Open DevTools** (F12) → **Console**
3. **Look for:**
   - `[API] Backend URL: https://nexhacks-nu.vercel.app` ✅
   - `[API] Fetching trending markets: ...` ✅
   - `[API] Trending markets received: ...` ✅
   - No CORS errors ✅
   - Extension overlay loads with data ✅

**✅ Success:** Extension loads data from production API  
**❌ Failure:** 
- `Failed to fetch` = CORS or URL issue
- `500` error = Backend issue
- No data = Database/API issue

---

## Advanced Testing

### Test All Endpoints

```powershell
$baseUrl = "https://nexhacks-nu.vercel.app"

# Test all endpoints
$endpoints = @(
    "/",
    "/test-cors",
    "/markets/trending?limit=3",
    "/gamma/tags",
    "/similar?event_title=test&limit=3"
)

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $endpoint" -ForegroundColor Cyan
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl$endpoint"
        Write-Host "  ✅ Success" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}
```

---

### Check Response Times

```powershell
$url = "https://nexhacks-nu.vercel.app/markets/trending?limit=5"

$times = @()
1..5 | ForEach-Object {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-RestMethod -Uri $url | Out-Null
        $stopwatch.Stop()
        $times += $stopwatch.ElapsedMilliseconds
        Write-Host "Request $_: $($stopwatch.ElapsedMilliseconds)ms"
    } catch {
        Write-Host "Request $_: FAILED"
    }
}

$avg = ($times | Measure-Object -Average).Average
Write-Host "Average response time: $([math]::Round($avg, 2))ms" -ForegroundColor Cyan
```

**Expected:** < 2 seconds for trending markets

---

## Troubleshooting

### If Root Endpoint Returns 500

1. **Check Vercel Logs:**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click on latest deployment → "Function Logs"
   - Look for Python errors

2. **Verify Environment Variables:**
   - Settings → Environment Variables
   - Must include:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
   - Must be set for **Production** environment

3. **Check Variable Names:**
   - Use `SUPABASE_ANON_KEY` (not `SUPABASE_KEY`)
   - Case-sensitive!

---

### If Database Endpoints Return 500

1. **Test Supabase Connection Locally:**
   ```powershell
   python -c "from database.supabase_connection import SupabaseConnection; c = SupabaseConnection(); print('✅ Connected')"
   ```

2. **Verify Keys:**
   - Go to Supabase Dashboard → Settings → API
   - Copy **anon public key** (not service_role)
   - Use this as `SUPABASE_ANON_KEY`

3. **Check Database Tables:**
   - Verify `markets` table exists
   - Verify `similarity_scores` table exists (if using similarity features)

---

### If CORS Errors Occur

1. **Verify CORS Middleware:**
   - Already configured in `api/main.py` ✅
   - Should allow all origins: `allow_origins=["*"]`

2. **Check Browser Console:**
   - Look for exact error message
   - Check if it's a preflight (OPTIONS) request issue

3. **Test with curl:**
   ```powershell
   curl -H "Origin: https://polymarket.com" -H "Access-Control-Request-Method: GET" -X OPTIONS "https://nexhacks-nu.vercel.app/markets/trending"
   ```

---

### If Extension Can't Connect

1. **Verify Environment Variable:**
   ```powershell
   cd Extension
   Get-Content .env.production
   # Should show: VITE_BACKEND=https://nexhacks-nu.vercel.app
   ```

2. **Rebuild Extension:**
   ```powershell
   npm run build:prod
   ```

3. **Reload Extension:**
   - Go to `chrome://extensions`
   - Click Reload

4. **Check Browser Console:**
   - Look for `[API] Backend URL:` log
   - Verify it shows the production URL

---

## Success Checklist

- [ ] Root endpoint returns 200 OK
- [ ] CORS test endpoint works
- [ ] Trending markets endpoint returns data
- [ ] Similar markets endpoint works
- [ ] No CORS errors in browser console
- [ ] Extension loads data from production API
- [ ] Response times are reasonable (< 2 seconds)
- [ ] All endpoints respond correctly

---

## Quick Reference

**Production URL:** `https://nexhacks-nu.vercel.app`

**Key Endpoints:**
- `/` - Root/health check
- `/test-cors` - CORS verification
- `/markets/trending` - Trending markets
- `/similar` - Similar markets
- `/related` - Related markets
- `/gamma/tags` - Market tags
- `/clob/price/{token_id}` - Price data

**Environment Variables Needed:**
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `GEMINI_API_KEY` (optional)

---

## Next Steps After Testing

1. ✅ If all tests pass → Extension is ready for production use
2. ✅ Monitor Vercel logs for any errors
3. ✅ Set up Vercel monitoring/alerts (optional)
4. ✅ Share production URL with team

---

Good luck! 🚀
