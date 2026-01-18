# 🔄 How to Reload Your Extension

## ✅ Extension Rebuilt Successfully!

The extension has been rebuilt with the production API URL: `https://nexhacks-nu.vercel.app`

---

## 📋 Step-by-Step Reload Instructions

### 1. Open Chrome Extensions Page
- **Option A**: Type `chrome://extensions/` in the address bar
- **Option B**: Click the three dots (⋮) → **Extensions** → **Manage extensions**

### 2. Enable Developer Mode
- Toggle **"Developer mode"** switch in the top-right corner (if not already enabled)

### 3. Find Your Extension
- Look for **"Polymarket Trade Assistant"** in the list
- Or look for the extension folder path: `c:\Users\shilo\NexHacks\NexHacks\Extension\dist`

### 4. Reload the Extension
- Click the **🔄 Reload** button (circular arrow icon) on your extension card
- Or click **"Remove"** then **"Load unpacked"** and select the `Extension\dist` folder

---

## 🧪 Testing Steps

### 1. Open Polymarket
- Go to: `https://polymarket.com`
- Navigate to any market page (e.g., search for a market)

### 2. Check Console for Errors
- Press **F12** to open DevTools
- Go to **Console** tab
- Look for:
  - ✅ `[API] Backend URL: https://nexhacks-nu.vercel.app`
  - ✅ Successful API calls (no CORS errors)
  - ✅ `[API] Fetching trending markets...`
  - ✅ `[API] Fetching similar markets...`

### 3. Verify Extension UI
- Look for the **NexHacks floating assistant** on the page
- Check that **Trending** and **Related** tabs load data
- Verify no error messages appear

---

## ✅ Expected Behavior

### What Should Work:
- ✅ Extension loads without errors
- ✅ Backend URL shows: `https://nexhacks-nu.vercel.app`
- ✅ Trending markets load successfully
- ✅ Related markets load when viewing a market page
- ✅ No CORS errors in console
- ✅ API calls return data (200 OK)

### What to Look For:
- **Console logs** showing successful API calls
- **Network tab** showing requests to `nexhacks-nu.vercel.app`
- **Extension UI** displaying market data

---

## 🐛 Troubleshooting

### If you see CORS errors:
- ✅ Make sure you're using the production URL (`nexhacks-nu.vercel.app`)
- ✅ Check that `manifest.json` has `https://*.vercel.app/*` in `host_permissions`

### If extension doesn't load:
- ✅ Make sure you're loading from `Extension\dist` folder
- ✅ Check that the build completed successfully
- ✅ Try removing and re-adding the extension

### If API calls fail:
- ✅ Check console for the backend URL (should be `https://nexhacks-nu.vercel.app`)
- ✅ Verify the API is working: `https://nexhacks-nu.vercel.app/`
- ✅ Check network tab for actual error messages

---

## 🎯 Quick Test Commands

After reloading, you can verify the extension is using the right URL:

1. **Open DevTools Console** (F12)
2. **Look for this log**: `[API] Backend URL: https://nexhacks-nu.vercel.app`
3. **If you see `localhost:8000`**, the extension wasn't rebuilt properly

---

## 📝 Summary

1. ✅ Extension rebuilt with production URL
2. 🔄 **Reload extension in Chrome** (`chrome://extensions/`)
3. 🌐 **Visit Polymarket** and test
4. 🔍 **Check console** for successful API calls

**You're ready to test!** 🚀
