# ⚡ Quick Reference - Chrome Extension Ready

## 🚀 Run Now (Copy & Paste)

### Terminal 1 - Start Backend
```
cd c:\Users\sinha\.vscode\NexHacks\backend
python run.py
```

### Terminal 2 - Open Chrome & Load Extension
1. Open Chrome
2. Paste in address bar: `chrome://extensions/`
3. Enable "Developer mode" (top right toggle)
4. Click "Load unpacked"
5. Navigate to: `c:\Users\sinha\.vscode\NexHacks\Extension\dist`
6. Select folder

---

## ✅ Verify It Works

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Go to https://polymarket.com | Page loads normally |
| 2 | Click on any market | Market page opens |
| 3 | Look at right side | Floating panel appears |
| 4 | Wait 2-3 sec | Recommendations load |
| 5 | See two sections | "If you like YES" & "If you like NO" |

---

## 📍 Key File Locations

- **Load this folder in Chrome**: `Extension\dist`
- **Run this file**: `backend\run.py`
- **Backend URL**: `http://localhost:8000`
- **Setup guide**: `CHROME_SETUP.md`
- **Testing guide**: `TESTING_FLAGS.md`

---

## 🔍 Troubleshooting

| Problem | Fix |
|---------|-----|
| Extension won't load | Make sure path is `Extension\dist` (not `Extension`) |
| No recommendations | Start backend: `python backend/run.py` |
| CORS errors | Backend CORS enabled by default |
| MongoDB error | MongoDB must run on localhost:27017 |

---

## 📊 What's Included

✅ Extension UI fully working  
✅ API integration complete  
✅ Type-safe TypeScript (0 errors)  
✅ Error handling with fallback  
✅ Market history tracking  
✅ Local profile extraction  
✅ Comprehensive logging  

---

## 🎯 In One Sentence

**Extension is built and ready** - just start backend and load `Extension\dist` folder in Chrome.

---

See [CHROME_SETUP.md](CHROME_SETUP.md) for detailed instructions.
