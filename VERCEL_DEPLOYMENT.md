# 🚀 Vercel Deployment Guide

## ✅ Pre-Deployment Checklist

Your codebase is now ready for Vercel! Here's what's been configured:

- ✅ `api/index.py` - Vercel entry point (exposes FastAPI app)
- ✅ `vercel.json` - Vercel configuration
- ✅ `pyproject.toml` - Python version specification (3.11)
- ✅ `api/requirements.txt` - All dependencies listed
- ✅ `.vercelignore` - Excludes unnecessary files
- ✅ CORS middleware configured
- ✅ All imports tested and working

---

## 📋 Deployment Steps

### **Step 1: Install Vercel CLI** (Optional but recommended)

```bash
npm install -g vercel
```

### **Step 2: Login to Vercel**

```bash
vercel login
```

### **Step 3: Test Build Locally** (Recommended)

```bash
# Test that imports work
cd c:\Users\shilo\NexHacks\NexHacks
python -c "from api.index import app; print('✅ Build test passed!')"

# Test with Vercel CLI (if installed)
vercel dev
```

### **Step 4: Deploy to Vercel**

**Option A: Using Vercel CLI**
```bash
vercel
# Follow prompts:
# - Link to existing project? No
# - Project name: nexhacks-api
# - Directory: ./
# - Override settings? No
```

**Option B: Using Vercel Dashboard**
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Vercel will auto-detect Python/FastAPI
5. Configure:
   - **Root Directory:** `./` (root of repo)
   - **Framework Preset:** Other
   - **Build Command:** (leave empty - Vercel handles Python)
   - **Output Directory:** (leave empty)
   - **Install Command:** (leave empty)

### **Step 5: Add Environment Variables**

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add these (get values from your `.env` file):
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_key (optional)
```

**Important:** The environment variable name is `SUPABASE_ANON_KEY` (not `SUPABASE_KEY`). This is the "anon public key" from your Supabase project settings.

**Important:** Add to **Production**, **Preview**, and **Development** environments.

### **Step 6: Deploy**

- If using CLI: `vercel --prod`
- If using Dashboard: Click "Deploy"

### **Step 7: Get Your API URL**

After deployment, Vercel will give you:
- **Production URL:** `https://nexhacks-api.vercel.app`
- **Preview URLs:** For each branch/PR

---

## 🔧 Configuration Files

### **`vercel.json`**
```json
{
  "version": 2,
  "functions": {
    "api/**/*.py": {
      "runtime": "@vercel/python",
      "maxDuration": 30
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### **`api/index.py`**
- Entry point for Vercel
- Imports FastAPI app from `api/main.py`
- Vercel automatically detects the `app` object

### **`pyproject.toml`**
- Specifies Python 3.11
- Vercel will use this version

---

## 🧪 Testing the Deployment

### **1. Test Root Endpoint**
```bash
curl https://your-app.vercel.app/
```

Expected:
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

### **2. Test CORS Endpoint**
```bash
curl https://your-app.vercel.app/test-cors
```

Expected:
```json
{
  "status": "ok",
  "cors": "enabled",
  "message": "CORS test successful"
}
```

### **3. Test Trending Markets**
```bash
curl https://your-app.vercel.app/markets/trending?limit=5
```

### **4. Test from Browser Console**
```javascript
// On any website (like polymarket.com)
fetch('https://your-app.vercel.app/markets/trending')
  .then(r => r.json())
  .then(console.log)
```

Should work without CORS errors! ✅

---

## 🔄 Update Extension for Production

After deployment, update your extension:

### **Method 1: Environment Variable**
```bash
cd Extension
VITE_BACKEND=https://your-app.vercel.app npm run build
```

### **Method 2: Create `.env.production`**
Create `Extension/.env.production`:
```
VITE_BACKEND=https://your-app.vercel.app
```

Then build:
```bash
npm run build -- --mode production
```

### **Method 3: Update `api.ts` Directly** (Quick test)
Temporarily update `Extension/src/utils/api.ts`:
```typescript
const BACKEND_BASE_URL = 'https://your-app.vercel.app';
```

---

## 🐛 Troubleshooting

### **Build Fails: "Cannot import module"**

**Fix:** Check that all imports in `api/main.py` are correct:
- `from polymarket.news import fetch_news` ✅
- `from services.trending import TrendingService` ✅
- `from api.clients.gamma_client import GammaClient` ✅

### **Build Fails: "Module not found"**

**Fix:** Ensure all dependencies are in `api/requirements.txt`

### **Runtime Error: "Environment variable not set"**

**Fix:** Add environment variables in Vercel dashboard:
- Settings → Environment Variables
- Add `SUPABASE_URL`, `SUPABASE_KEY`, etc.

### **CORS Errors Still Happening**

**Fix:** 
- Check CORS middleware is configured (it is ✅)
- Verify API URL is HTTPS (Vercel provides HTTPS automatically)
- Check browser console for exact error

### **Function Timeout**

**Fix:** Increase `maxDuration` in `vercel.json`:
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "@vercel/python",
      "maxDuration": 60  // Increase to 60 seconds
    }
  }
}
```

---

## 📊 Vercel Limits

- **Free Tier:**
  - 100GB bandwidth/month
  - Serverless function execution time: 10s (Hobby), 60s (Pro)
  - 100 serverless function invocations/day (Hobby)

- **Pro Tier ($20/month):**
  - Unlimited bandwidth
  - 60s execution time
  - Unlimited invocations

**Your API should work fine on Free tier!** ✅

---

## ✅ Post-Deployment Checklist

- [ ] API deployed successfully
- [ ] Root endpoint (`/`) returns JSON
- [ ] CORS test endpoint works
- [ ] Trending markets endpoint works
- [ ] Environment variables set in Vercel
- [ ] Extension rebuilt with production URL
- [ ] Extension reloaded in Chrome
- [ ] Tested on Polymarket - no CORS errors!

---

## 🎯 Quick Deploy Command

```bash
# One command to deploy (if Vercel CLI installed)
vercel --prod
```

---

## 📝 Files Created/Modified

- ✅ `api/index.py` - Vercel entry point
- ✅ `vercel.json` - Updated for Vercel
- ✅ `pyproject.toml` - Python version
- ✅ `.vercelignore` - Exclude unnecessary files
- ✅ `api/main.py` - Fixed imports, made logging Vercel-safe
- ✅ `api/requirements.txt` - All dependencies

---

## 🚀 You're Ready!

Your codebase is fully prepared for Vercel deployment. Just:

1. Push to GitHub
2. Connect to Vercel
3. Add environment variables
4. Deploy!

**Your API will be live at:** `https://your-app.vercel.app` 🎉
