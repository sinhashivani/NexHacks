# 🚀 Deployment Guide - Hosting Your API Publicly

## Why Deploy Publicly?

Hosting your FastAPI backend publicly solves:
- ✅ **CORS issues** - No more "unknown address space" errors
- ✅ **Chrome privacy policies** - HTTPS to HTTPS is always allowed
- ✅ **Production ready** - Users can use your extension without running localhost
- ✅ **Better performance** - Cloud hosting is faster than localhost

---

## 🎯 Quick Deploy Options

### **Option 1: Render (Recommended - Easiest)**

**Steps:**

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to Render Dashboard:**
   - Visit: https://render.com
   - Sign up/login (free tier available)

3. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

4. **Configure Service:**
   - **Name:** `nexhacks-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r api/requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** Leave empty (or set to repo root)

5. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable"
   
   Add these (get values from your `.env` file):
   ```
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_key_here
   GEMINI_API_KEY=your_gemini_key_here (optional)
   ```
   
   **Important:** Mark these as "Secret" (they won't be visible in logs)

6. **Deploy:**
   - Click "Create Web Service"
   - Wait 2-5 minutes for build
   - Your API will be live at: `https://nexhacks-api.onrender.com`

7. **Update Extension:**
   - Create `Extension/.env.production`:
     ```
     VITE_BACKEND=https://nexhacks-api.onrender.com
     ```
   - Or build with: `VITE_BACKEND=https://nexhacks-api.onrender.com npm run build`

---

### **Option 2: Railway (Also Easy)**

**Steps:**

1. **Install Railway CLI** (optional, can use web UI):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy:**
   ```bash
   railway init
   railway up
   ```

3. **Set Environment Variables:**
   - Go to Railway dashboard
   - Add `SUPABASE_URL`, `SUPABASE_KEY`, etc.

4. **Get Your URL:**
   - Railway gives you: `https://your-app.railway.app`

---

### **Option 3: Fly.io (More Control)**

**Steps:**

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Initialize:**
   ```bash
   cd api
   fly launch
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

---

## 📝 Pre-Deployment Checklist

### **1. Update render.yaml (if using Render)**

Your `render.yaml` is already configured! Just add environment variables in the dashboard.

### **2. Verify Environment Variables**

Make sure these are set in your hosting platform:
- ✅ `SUPABASE_URL` - Your Supabase project URL
- ✅ `SUPABASE_KEY` - Your Supabase anon key
- ✅ `GEMINI_API_KEY` - (Optional) For AI features

### **3. Test Locally First**

```bash
# Make sure your API works locally
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/markets/trending
```

---

## 🔧 Update Extension for Production

### **Method 1: Environment Variable (Recommended)**

Create `Extension/.env.production`:
```env
VITE_BACKEND=https://your-api-url.onrender.com
```

Then build:
```bash
cd Extension
npm run build -- --mode production
```

### **Method 2: Hardcode for Production Build**

Update `Extension/src/utils/api.ts`:
```typescript
// For production builds, use public API
const BACKEND_BASE_URL = 
  import.meta.env.PROD 
    ? 'https://your-api-url.onrender.com'  // Production
    : (import.meta.env.VITE_BACKEND || 'http://localhost:8000');  // Development
```

### **Method 3: Build Scripts**

Add to `Extension/package.json`:
```json
{
  "scripts": {
    "build": "vite build",
    "build:prod": "VITE_BACKEND=https://your-api-url.onrender.com vite build",
    "build:dev": "VITE_BACKEND=http://localhost:8000 vite build"
  }
}
```

Then:
```bash
npm run build:prod  # For production
npm run build:dev   # For development
```

---

## ✅ Post-Deployment Steps

### **1. Test Your Deployed API**

```bash
# Test root endpoint
curl https://your-api-url.onrender.com/

# Test trending markets
curl https://your-api-url.onrender.com/markets/trending

# Test CORS (from browser console on any site)
fetch('https://your-api-url.onrender.com/markets/trending')
  .then(r => r.json())
  .then(console.log)
```

### **2. Update Extension**

1. Build extension with production URL:
   ```bash
   cd Extension
   VITE_BACKEND=https://your-api-url.onrender.com npm run build
   ```

2. Reload extension in Chrome:
   - Go to `chrome://extensions/`
   - Click reload on your extension

3. Test on Polymarket:
   - Navigate to `https://polymarket.com`
   - Open extension
   - Check console - should see API calls to your production URL
   - No CORS errors!

### **3. Monitor Your API**

- **Render:** Check dashboard for logs and metrics
- **Railway:** View logs in dashboard
- **Fly.io:** `fly logs` command

---

## 🐛 Troubleshooting

### **Issue: API returns 500 errors**

**Check:**
- Environment variables are set correctly
- Supabase credentials are valid
- Check deployment logs for Python errors

### **Issue: Extension still uses localhost**

**Fix:**
- Rebuild extension with production URL
- Clear browser cache
- Reload extension

### **Issue: CORS errors persist**

**Fix:**
- Your CORS middleware is already configured
- Make sure API URL is HTTPS (not HTTP)
- Check browser console for exact error

### **Issue: Build fails on Render**

**Check:**
- `api/requirements.txt` exists and is correct
- Python version matches (3.11.0)
- Build logs show specific error

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Render** | ✅ Free (spins down after inactivity) | $7/month (always on) |
| **Railway** | ✅ $5 free credits/month | Pay as you go |
| **Fly.io** | ✅ Free (limited resources) | $1.94/month+ |
| **Vercel** | ✅ Free (serverless) | $20/month+ |

**Recommendation:** Start with Render free tier, upgrade to paid if you need always-on.

---

## 🎯 Quick Start (Render)

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push

# 2. Go to render.com, connect repo, deploy

# 3. Add environment variables in Render dashboard

# 4. Wait for deployment (2-5 min)

# 5. Update extension
cd Extension
VITE_BACKEND=https://your-app.onrender.com npm run build

# 6. Reload extension in Chrome

# 7. Test! 🎉
```

---

## 📊 What Gets Deployed

- ✅ FastAPI backend (`api/main.py`)
- ✅ All API endpoints (`/markets/trending`, `/similar`, `/related`, `/news`, etc.)
- ✅ Advanced endpoints (`/gamma/*`, `/clob/*`, `/ai/*`)
- ✅ CORS middleware (configured for all origins)
- ✅ All dependencies from `api/requirements.txt`

**Not deployed:**
- Extension code (stays local, built separately)
- Database (Supabase is already hosted)
- Local `.env` files (use platform's env vars)

---

## 🔐 Security Notes

1. **Never commit `.env` files** - Already in `.gitignore` ✅
2. **Use Secret environment variables** - Mark sensitive vars as "Secret" in Render
3. **HTTPS only** - All platforms provide HTTPS automatically
4. **CORS is configured** - Already allows all origins (you can restrict later)

---

## 🎉 Success!

Once deployed, your extension will:
- ✅ Work for all users (no localhost needed)
- ✅ No CORS errors
- ✅ Faster API responses
- ✅ Production-ready

**Your API URL will be:** `https://nexhacks-api.onrender.com` (or similar)

**Update extension with:** `VITE_BACKEND=https://your-url npm run build`

---

**Need help?** Check deployment logs in your platform's dashboard for specific errors.
