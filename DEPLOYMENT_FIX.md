# 🔧 Render Deployment Fix

## Problem
Build error: `Cannot import 'setuptools.build_meta'` - Render was using Python 3.13 instead of 3.11.

## ✅ Fixes Applied

1. **Added `runtime.txt`** - Forces Python 3.11.0
2. **Updated `render.yaml`** - Added `pythonVersion: 3.11.0` explicitly
3. **Updated build command** - Upgrades pip/setuptools/wheel first
4. **Added setuptools to requirements.txt** - Ensures it's installed

## 🚀 Next Steps

1. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "Fix Render deployment - Python 3.11 and setuptools"
   git push
   ```

2. **In Render Dashboard:**
   - Go to your service settings
   - Make sure **Python Version** is set to **3.11.0**
   - If it's set to 3.13, change it to 3.11.0
   - Save changes

3. **Redeploy:**
   - Render should auto-deploy after push
   - Or click "Manual Deploy" → "Deploy latest commit"

4. **Check build logs:**
   - Should see: "Using Python 3.11.0"
   - Should see: "Installing setuptools..."
   - Build should succeed!

## 📝 Files Changed

- ✅ `render.yaml` - Added `pythonVersion: 3.11.0`
- ✅ `runtime.txt` - Created (Python 3.11.0)
- ✅ `api/requirements.txt` - Added setuptools and wheel

## 🐛 If Still Failing

If you still get errors, try this in Render dashboard:

1. **Go to Environment tab**
2. **Add environment variable:**
   - Key: `PYTHON_VERSION`
   - Value: `3.11.0`
   - Save

3. **Or use this build command instead:**
   ```
   python3.11 -m pip install --upgrade pip setuptools wheel && python3.11 -m pip install -r api/requirements.txt
   ```

---

**The build should work now!** 🎉
