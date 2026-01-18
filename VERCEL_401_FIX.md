# 🔧 Fixing 401 Unauthorized Error on Vercel

## Problem

You're getting `401 Unauthorized` errors when trying to access your Vercel deployment. This is **NOT** a problem with your FastAPI code - it's a Vercel configuration issue.

## Root Cause

Vercel has **Deployment Protection** enabled, which requires authentication to access preview deployments. This is a security feature that blocks public access.

## Solution: Disable Deployment Protection

### Option 1: Disable for Preview Deployments (Recommended)

1. Go to **Vercel Dashboard** → Your Project
2. Click **Settings** → **Deployment Protection**
3. Find **"Preview Deployments"** section
4. Change from **"Password Protected"** or **"Vercel Authentication"** to **"None"**
5. Save changes

### Option 2: Use Production Deployment

If you want to keep protection on previews, deploy to production:

```bash
vercel --prod
```

Production deployments are usually public by default.

### Option 3: Get Production URL

1. Go to **Vercel Dashboard** → Your Project
2. Look for the **Production** deployment (not Preview)
3. Copy the production URL (usually `https://your-project-name.vercel.app`)
4. Use that URL instead of the preview URL

---

## How to Check Your Deployment Type

**Preview URLs look like:**
- `https://nexhacks-[random-hash]-[username].vercel.app`
- `https://your-project-git-[branch]-[username].vercel.app`

**Production URLs look like:**
- `https://your-project-name.vercel.app`
- `https://nexhacks.vercel.app` (if you set a custom domain)

---

## Quick Fix Steps

1. **Go to Vercel Dashboard:**
   - https://vercel.com/dashboard
   - Select your project

2. **Check Deployment Protection:**
   - Settings → Deployment Protection
   - Or Settings → General → Deployment Protection

3. **Disable for Preview:**
   - Set Preview Deployments to "None"
   - Keep Production as "None" (should already be)

4. **Redeploy or Use Production:**
   - Either redeploy: `vercel --prod`
   - Or use the production URL from dashboard

---

## Alternative: Test with Production URL

If you have a production deployment, update the test script:

```powershell
.\test_vercel.ps1 -ApiUrl "https://your-production-url.vercel.app"
```

---

## Verify Fix

After disabling protection, test again:

```powershell
.\test_vercel.ps1
```

You should now get `200 OK` responses instead of `401 Unauthorized`.

---

## Why This Happens

Vercel enables deployment protection by default for:
- **Preview deployments** (from branches/PRs) - to prevent unauthorized access
- **Team projects** - to control who can access previews

Your FastAPI app doesn't have authentication - this is purely a Vercel security feature.

---

## Additional Notes

- **Production deployments** are usually public by default
- **Preview deployments** can be protected
- This is a **Vercel setting**, not a code issue
- Your FastAPI app is fine - it's just blocked by Vercel's protection

---

## Still Getting 401?

If you've disabled protection and still get 401:

1. **Check you're using the right URL** (production vs preview)
2. **Wait a few minutes** for settings to propagate
3. **Redeploy** after changing settings
4. **Check Vercel logs** for more details
5. **Try accessing in incognito/private browser** (in case of cached auth)

---

## Fixed PowerShell Script

I've also fixed the PowerShell script error (`System.Web.HttpUtility` not found). The script now uses `[System.Uri]::EscapeDataString()` which works in PowerShell Core.

Run the test again after fixing the deployment protection!
