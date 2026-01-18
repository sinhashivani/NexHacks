# 🔧 Vercel Deployment Fix

## Issue Fixed

The deployment was failing with:
```
ValueError: Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file
```

## Root Causes

1. **Services initialized at import time** - `TrendingService()` and `PolymarketAPIService()` were being created when the module was imported, causing failures if environment variables weren't set yet.

2. **Environment variable name mismatch** - Documentation mentioned `SUPABASE_KEY` but code expects `SUPABASE_ANON_KEY`.

## Fixes Applied

### ✅ 1. Made Service Initialization Lazy

Changed from:
```python
# OLD - Initialized at import time (fails if env vars missing)
trending_service = TrendingService()
polymarket_api = PolymarketAPIService()
```

To:
```python
# NEW - Lazy initialization (only when first used)
_trending_service: Optional[TrendingService] = None
_polymarket_api: Optional[PolymarketAPIService] = None

def get_trending_service() -> TrendingService:
    """Get or create TrendingService instance"""
    global _trending_service
    if _trending_service is None:
        _trending_service = TrendingService()
    return _trending_service

def get_polymarket_api() -> PolymarketAPIService:
    """Get or create PolymarketAPIService instance"""
    global _polymarket_api
    if _polymarket_api is None:
        _polymarket_api = PolymarketAPIService()
    return _polymarket_api
```

Now services are only created when endpoints actually use them, not at import time.

### ✅ 2. Updated Environment Variable Name

Fixed documentation to use the correct variable name:
- **Correct:** `SUPABASE_ANON_KEY`
- **Wrong:** `SUPABASE_KEY`

## Required Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GEMINI_API_KEY=your_gemini_key (optional)
```

**Important:** 
- Use `SUPABASE_ANON_KEY` (not `SUPABASE_KEY`)
- This is the "anon public key" from Supabase Settings → API
- Add to **Production**, **Preview**, and **Development** environments

## Testing

After adding environment variables in Vercel:

1. **Redeploy** your application
2. **Test root endpoint:**
   ```bash
   curl https://your-app.vercel.app/
   ```
3. **Test trending endpoint:**
   ```bash
   curl https://your-app.vercel.app/markets/trending?limit=5
   ```

## Files Modified

- ✅ `api/main.py` - Made service initialization lazy
- ✅ `VERCEL_DEPLOYMENT.md` - Fixed env var name
- ✅ `VERCEL_READY.md` - Fixed env var name

## Next Steps

1. **Add environment variables** in Vercel dashboard (use `SUPABASE_ANON_KEY`)
2. **Redeploy** your application
3. **Test endpoints** to verify everything works

The app should now start successfully even if environment variables aren't set initially, and will only fail when endpoints that require them are called.
