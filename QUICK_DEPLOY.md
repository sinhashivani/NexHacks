# 🚀 Quick Deployment Guide

## Two Options: Localhost Fix vs Public Hosting

### **Option A: Test Localhost Fixes First** (5 minutes)

The fixes I added should work! Test them:

1. **Restart backend** (if not auto-reloaded):
   ```bash
   cd api
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Rebuild extension**:
   ```bash
   cd Extension
   npm run build
   ```

3. **Reload extension** in Chrome (`chrome://extensions/` → reload)

4. **Test on Polymarket** - CORS errors should be gone!

---

### **Option B: Deploy Publicly** (15 minutes, Production-Ready)

**Why:** Eliminates all CORS issues, works for all users, production-ready.

#### **Step 1: Deploy to Render** (Free)

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Go to Render.com:**
   - Sign up/login (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

3. **Configure:**
   - **Name:** `nexhacks-api`
   - **Build Command:** `pip install -r api/requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** (in Render dashboard):
   - `SUPABASE_URL` = (from your `.env` file)
   - `SUPABASE_KEY` = (from your `.env` file)
   - `GEMINI_API_KEY` = (optional, from your `.env` file)

5. **Deploy** - Wait 2-5 minutes

6. **Get Your URL:** `https://nexhacks-api.onrender.com` (or similar)

#### **Step 2: Update Extension**

```bash
cd Extension
VITE_BACKEND=https://nexhacks-api.onrender.com npm run build
```

#### **Step 3: Reload Extension**

- Go to `chrome://extensions/`
- Click reload on your extension
- Test on Polymarket!

---

## 🎯 Recommendation

**Try Option A first** (localhost fixes) - they should work now with:
- ✅ CORS middleware configured
- ✅ Private Network Access header added
- ✅ Extension manifest updated

**If Option A doesn't work**, go with **Option B** (public hosting) - it's more reliable and production-ready anyway!

---

## 📝 Full Deployment Guide

See `docs/DEPLOYMENT_GUIDE.md` for detailed instructions on:
- Render, Railway, Fly.io options
- Environment variable setup
- Troubleshooting
- Cost comparison

---

**Quick Test Command:**
```bash
# After deployment, test your API:
curl https://your-api-url.onrender.com/markets/trending
```
