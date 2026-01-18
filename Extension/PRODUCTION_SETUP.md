# ✅ Extension Production Setup Complete

## What Was Done

1. ✅ Created `.env.production` with production URL: `https://nexhacks.vercel.app`
2. ✅ Updated `package.json` build script for production mode
3. ✅ Updated `manifest.json` to allow requests to `*.vercel.app` domains
4. ✅ Built extension with production configuration

## Next Steps

### Step 1: Verify Production URL in Vercel

Make sure your production deployment is live:
- Go to Vercel Dashboard → Your Project
- Check the **Production** deployment URL (should be `https://nexhacks.vercel.app`)
- If it's different, update `.env.production` with the correct URL

### Step 2: Reload Extension in Chrome

1. Open Chrome
2. Go to `chrome://extensions`
3. Find your extension
4. Click the **Reload** button (🔄)
5. Or toggle it off and back on

### Step 3: Test on Polymarket

1. Visit any Polymarket market page (e.g., `https://polymarket.com/event/...`)
2. Open DevTools (F12) → Console tab
3. Look for:
   - `[API] Backend URL: https://nexhacks.vercel.app` ✅
   - Successful API calls (no CORS errors)
   - Data loading in the extension overlay

### Step 4: Verify API Connection

In browser console, run:
```javascript
fetch('https://nexhacks.vercel.app/markets/trending?limit=5')
  .then(r => r.json())
  .then(data => console.log('✅ API Working:', data))
  .catch(err => console.error('❌ Error:', err))
```

**Expected:** Should return market data without errors

---

## If You Want to Use a Different URL

If you need to use a different Vercel URL (like a preview URL):

1. **Update `.env.production`:**
   ```
   VITE_BACKEND=https://your-preview-url.vercel.app
   ```

2. **Rebuild:**
   ```bash
   cd Extension
   npm run build:prod
   ```

3. **Reload extension**

**Note:** Preview URLs may have 401 errors due to Vercel deployment protection. Use production URL for best results.

---

## Files Modified

- ✅ `Extension/.env.production` - Production API URL
- ✅ `Extension/package.json` - Updated build script
- ✅ `Extension/src/manifest.json` - Added vercel.app permissions
- ✅ `Extension/dist/` - Rebuilt with production config

---

## Troubleshooting

### Extension Still Using Localhost?

1. Make sure you reloaded the extension after rebuild
2. Check browser console for `[API] Backend URL:` log
3. Clear browser cache and reload

### CORS Errors?

1. Verify production URL is correct in `.env.production`
2. Check Vercel deployment is live and accessible
3. Verify `manifest.json` has `*.vercel.app` in `host_permissions`

### 401 Unauthorized?

- This means you're using a preview URL with protection enabled
- Use production URL instead: `https://nexhacks.vercel.app`
- Or disable deployment protection in Vercel dashboard

---

## Quick Commands

```bash
# Rebuild for production
cd Extension
npm run build:prod

# Rebuild for development (localhost)
npm run build:dev

# Regular build (uses .env or defaults)
npm run build
```

---

## ✅ You're Ready!

Your extension is now configured to use the production Vercel API. Just reload it in Chrome and test on Polymarket!
