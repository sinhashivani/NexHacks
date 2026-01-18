# 🧪 Vercel Deployment Testing Guide

## Quick Start Testing

### Step 1: Get Your Vercel URL

Your API should be deployed at:
- **Production:** `https://nexhacks-[hash].vercel.app` or `https://your-project-name.vercel.app`
- **Preview:** Check Vercel dashboard for preview URLs

---

## ✅ Phase 1: Basic Connectivity Tests

### Test 1: Root Endpoint

```bash
# Using curl
curl https://your-app.vercel.app/

# Expected response:
{
  "name": "NexHacks Polymarket API",
  "version": "1.0.0",
  "endpoints": {
    "trending": "/markets/trending",
    "ui": "/ui"
  }
}
```

**✅ Success:** JSON response with API info  
**❌ Failure:** 500 error = Check environment variables

---

### Test 2: Health Check (CORS Test Endpoint)

```bash
curl https://your-app.vercel.app/test-cors

# Expected response:
{
  "status": "ok",
  "cors": "enabled",
  "message": "CORS test successful"
}
```

**✅ Success:** Returns 200 OK with CORS message  
**❌ Failure:** 500 error = Check app initialization

---

### Test 3: Favicon Handler

```bash
curl -I https://your-app.vercel.app/favicon.ico

# Expected response:
HTTP/1.1 204 No Content
```

**✅ Success:** 204 No Content (no more 404s!)  
**❌ Failure:** 404 = Favicon handler not deployed yet

---

## ✅ Phase 2: Database Connectivity Tests

### Test 4: Trending Markets (Requires Database)

```bash
curl https://your-app.vercel.app/markets/trending?limit=5

# Expected response:
{
  "count": 5,
  "markets": [
    {
      "question": "...",
      "slug": "...",
      ...
    }
  ]
}
```

**✅ Success:** Returns markets array  
**❌ Failure:** 
- `500 Internal Server Error` = Database connection issue
- Check `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Vercel dashboard

---

### Test 5: Similar Markets (Requires Database)

```bash
curl "https://your-app.vercel.app/similar?event_title=Who+will+Trump+nominate+as+Fed+Chair%3F&limit=5"

# Expected response:
{
  "event_title": "Who will Trump nominate as Fed Chair?",
  "similar_markets": [...]
}
```

**✅ Success:** Returns similar markets  
**❌ Failure:** 500 error = Database or similarity_scores table issue

---

## ✅ Phase 3: CORS Testing (Browser)

### Test 6: CORS from Browser Console

1. Open any website (e.g., `https://polymarket.com`)
2. Open browser DevTools (F12)
3. Go to Console tab
4. Run:

```javascript
fetch('https://your-app.vercel.app/markets/trending?limit=5')
  .then(r => r.json())
  .then(data => console.log('✅ Success:', data))
  .catch(err => console.error('❌ Error:', err))
```

**✅ Success:** Data logged to console, no CORS errors  
**❌ Failure:** 
- `CORS policy` error = CORS middleware issue
- `Failed to fetch` = Network/URL issue
- `500` error = Backend issue

---

### Test 7: CORS Preflight Test

```javascript
fetch('https://your-app.vercel.app/markets/trending', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'X-Custom-Header': 'test'
  }
})
  .then(r => r.json())
  .then(data => console.log('✅ Preflight OK:', data))
  .catch(err => console.error('❌ Preflight failed:', err))
```

**✅ Success:** Request succeeds  
**❌ Failure:** CORS headers not configured correctly

---

## ✅ Phase 4: Advanced API Tests

### Test 8: Gamma API Endpoints (Requires API Keys)

```bash
# Get all tags
curl https://your-app.vercel.app/gamma/tags

# Get markets by tag
curl https://your-app.vercel.app/gamma/events/by-tag/politics
```

**✅ Success:** Returns tags/events  
**❌ Failure:** 500 error = Gamma API client issue (may need API key)

---

### Test 9: CLOB Price Endpoints

```bash
# Get price for a token (replace TOKEN_ID)
curl https://your-app.vercel.app/clob/price/TOKEN_ID
```

**✅ Success:** Returns price data  
**❌ Failure:** 500 error = CLOB client issue

---

### Test 10: AI Endpoints (Requires GEMINI_API_KEY)

```bash
# Semantic similarity
curl -X POST https://your-app.vercel.app/ai/semantic-similarity \
  -H "Content-Type: application/json" \
  -d '{"market1": "Who will win?", "market2": "Who will lose?"}'
```

**✅ Success:** Returns similarity score  
**❌ Failure:** 500 error = Missing `GEMINI_API_KEY` or AI client issue

---

## ✅ Phase 5: Frontend Integration Test

### Test 11: Update Extension to Use Production URL

1. **Update Extension Configuration:**

   Create `Extension/.env.production`:
   ```
   VITE_BACKEND=https://your-app.vercel.app
   ```

2. **Rebuild Extension:**
   ```bash
   cd Extension
   npm run build -- --mode production
   ```

3. **Reload Extension in Chrome:**
   - Go to `chrome://extensions`
   - Click "Reload" on your extension

4. **Test on Polymarket:**
   - Visit any Polymarket market page
   - Extension should load trending/similar markets
   - Check browser console for errors

**✅ Success:** Extension loads data from Vercel API  
**❌ Failure:** 
- `Failed to fetch` = CORS or URL issue
- `500` error = Backend issue
- No data = Database/API issue

---

## 🔍 Troubleshooting Checklist

### If Root Endpoint Returns 500:

1. ✅ Check Vercel logs: Dashboard → Your Project → Logs
2. ✅ Verify environment variables are set:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `GEMINI_API_KEY` (optional)
3. ✅ Check variable names match exactly (case-sensitive)
4. ✅ Verify variables are added to **Production** environment

### If Database Endpoints Return 500:

1. ✅ Test Supabase connection locally:
   ```bash
   python -c "from database.supabase_connection import SupabaseConnection; c = SupabaseConnection(); print('✅ Connected')"
   ```
2. ✅ Verify `SUPABASE_ANON_KEY` is the **anon public key** (not service_role)
3. ✅ Check Supabase dashboard → Settings → API for correct keys
4. ✅ Verify database tables exist (markets, similarity_scores, etc.)

### If CORS Errors Occur:

1. ✅ Verify CORS middleware is configured (it is ✅)
2. ✅ Check `Access-Control-Allow-Origin` header in response
3. ✅ Verify extension `manifest.json` has correct permissions
4. ✅ Test with browser console to see exact error

### If Extension Can't Connect:

1. ✅ Verify `VITE_BACKEND` is set correctly in `.env.production`
2. ✅ Rebuild extension after changing env vars
3. ✅ Check browser console for exact error message
4. ✅ Verify extension is reloaded after rebuild

---

## 📊 Expected Response Times

- **Root endpoint:** < 100ms
- **Trending markets:** < 2 seconds
- **Similar markets:** < 3 seconds
- **Gamma API calls:** < 2 seconds
- **AI endpoints:** < 5 seconds

If responses are slower, check:
- Database query performance
- API rate limits
- Network latency

---

## ✅ Success Criteria

Your deployment is successful when:

- [x] Root endpoint returns 200 OK
- [x] CORS test endpoint works
- [x] Trending markets endpoint returns data
- [x] Similar markets endpoint works
- [x] No CORS errors in browser console
- [x] Extension loads data from production API
- [x] All endpoints respond in reasonable time

---

## 🚀 Quick Test Script

Save this as `test_vercel.sh`:

```bash
#!/bin/bash

API_URL="https://your-app.vercel.app"

echo "Testing Vercel Deployment..."
echo "================================"

echo "1. Root endpoint..."
curl -s "$API_URL/" | head -5

echo -e "\n2. CORS test..."
curl -s "$API_URL/test-cors"

echo -e "\n3. Trending markets..."
curl -s "$API_URL/markets/trending?limit=3" | head -10

echo -e "\n4. Favicon..."
curl -I -s "$API_URL/favicon.ico" | head -1

echo -e "\n================================"
echo "Tests complete!"
```

Or for PowerShell (`test_vercel.ps1`):

```powershell
$API_URL = "https://your-app.vercel.app"

Write-Host "Testing Vercel Deployment..."
Write-Host "================================"

Write-Host "`n1. Root endpoint..."
Invoke-RestMethod -Uri "$API_URL/" | ConvertTo-Json

Write-Host "`n2. CORS test..."
Invoke-RestMethod -Uri "$API_URL/test-cors" | ConvertTo-Json

Write-Host "`n3. Trending markets..."
$trending = Invoke-RestMethod -Uri "$API_URL/markets/trending?limit=3"
Write-Host "Found $($trending.count) markets"

Write-Host "`n================================"
Write-Host "Tests complete!"
```

---

## 📝 Next Steps After Testing

1. **If all tests pass:**
   - ✅ Update extension to use production URL
   - ✅ Deploy extension update
   - ✅ Monitor Vercel logs for errors
   - ✅ Set up Vercel monitoring/alerts

2. **If tests fail:**
   - Check `VERCEL_FIX.md` for common issues
   - Review Vercel logs for specific errors
   - Verify environment variables
   - Test locally first to isolate issues

---

## 🎯 Quick Reference

**Your API URL:** `https://your-app.vercel.app`

**Key Endpoints:**
- `/` - Root/health check
- `/test-cors` - CORS verification
- `/markets/trending` - Trending markets
- `/similar` - Similar markets
- `/gamma/tags` - Market tags
- `/clob/price/{token_id}` - Price data
- `/ai/similar` - AI recommendations

**Environment Variables Needed:**
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `GEMINI_API_KEY` (optional)

---

Good luck! 🚀
