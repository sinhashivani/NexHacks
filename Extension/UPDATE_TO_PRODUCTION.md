# 🔄 Update Extension to Production API

## ✅ What Was Done

1. ✅ Updated `.env.production` with production URL: `https://nexhacks-nu.vercel.app`
2. ✅ Rebuilt extension with production configuration
3. ✅ Verified production URL is in built files

---

## 📋 Next Steps

### Step 1: Reload Extension in Chrome

1. **Open Chrome Extensions:**
   - Go to `chrome://extensions`
   - Or: Menu (⋮) → Extensions → Manage Extensions

2. **Find Your Extension:**
   - Look for "Polymarket Trade Assistant"

3. **Reload the Extension:**
   - Click the **Reload** button (🔄) on your extension
   - Or toggle it off and back on

### Step 2: Test on Polymarket

1. **Visit a Polymarket Market Page:**
   - Go to: `https://polymarket.com/event/who-will-trump-nominate-as-fed-chair`
   - Or any other market page

2. **Open DevTools:**
   - Press `F12` or Right-click → Inspect
   - Go to **Console** tab

3. **Look for:**
   - `[API] Backend URL: https://nexhacks-nu.vercel.app` ✅
   - `[API] Fetching trending markets: ...` ✅
   - `[API] Trending markets received: ...` ✅
   - No CORS errors ✅
   - Extension overlay loads with data ✅

### Step 3: Verify API Connection

In the browser console, run:

```javascript
fetch('https://nexhacks-nu.vercel.app/markets/trending?limit=5')
  .then(r => r.json())
  .then(data => {
    console.log('✅ API Working:', data);
    console.log('✅ Markets found:', data.count);
  })
  .catch(err => console.error('❌ Error:', err))
```

**Expected:** Should return market data without errors

---

## 🔍 Troubleshooting

### Extension Still Using Localhost?

1. **Make sure you reloaded** the extension after rebuild
2. **Check browser console** for `[API] Backend URL:` log
3. **Clear browser cache** and reload

### CORS Errors?

1. Verify production URL is correct: `https://nexhacks-nu.vercel.app`
2. Check `manifest.json` has `*.vercel.app` in `host_permissions`
3. Verify extension is reloaded

### No Data Loading?

1. **Check console** for error messages
2. **Verify API is accessible:**
   ```javascript
   fetch('https://nexhacks-nu.vercel.app/')
     .then(r => r.json())
     .then(console.log)
   ```
3. **Check network tab** in DevTools for failed requests

---

## ✅ Verification Checklist

- [ ] Extension reloaded in Chrome
- [ ] Console shows production URL: `https://nexhacks-nu.vercel.app`
- [ ] No CORS errors in console
- [ ] Trending markets load in extension
- [ ] Similar markets load when on market page
- [ ] Data displays correctly in overlay

---

## 🎯 Quick Reference

**Production API URL:** `https://nexhacks-nu.vercel.app`

**Extension Files Updated:**
- ✅ `Extension/.env.production` - Production URL
- ✅ `Extension/dist/` - Rebuilt with production config

**To Rebuild Again:**
```powershell
cd Extension
npm run build:prod
```

---

Your extension is now configured to use the production API! 🚀
