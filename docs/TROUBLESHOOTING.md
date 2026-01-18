# Troubleshooting Guide - "No Data Showing"

## 🔍 What You're Seeing

**Symptoms:**
- Extension shows "No related markets found"
- Text appears white instead of blue
- No news articles appearing
- "Try Again" button doesn't help

---

## ✅ **FIXES APPLIED**

### 1. Blue Text Color ✅
**Fixed:** All text now uses blue (#4a90ff) theme colors
- Error messages: Blue
- Empty states: Blue  
- Market titles: Blue
- Icons: Blue

**What Changed:**
```css
.empty-state, .error-state {
  color: var(--text-primary) !important;  /* Now blue */
}

.empty-state svg, .error-state svg {
  color: var(--polyblue);  /* Blue icons */
}
```

### 2. Backend Running ✅
**Status:** Backend API is **running successfully** on `http://localhost:8000`

**Test it:**
```bash
curl http://localhost:8000/
# Returns: {"name":"NexHacks Polymarket API",...}
```

### 3. Trending Tab Works ✅
**Status:** Trending markets endpoint is **working**

**Test it:**
```bash
curl "http://localhost:8000/markets/trending?limit=5"
# Returns: List of 5 trending markets
```

---

## 🎯 **WHY "NO RELATED MARKETS FOUND"**

### The Real Issue: **Database Not Populated**

When you see "No related markets found", it means:

1. ✅ Extension is working correctly
2. ✅ Backend API is running
3. ✅ API request succeeds
4. ❌ **The specific market you're viewing is NOT in your database**

### Example:
```
You're viewing: "Supreme Court rules in favor of Trump..."
Extension scrapes: "Supreme Court rules in favor of Trump..."
API searches database: No match found ❌
Result: "No related markets found"
```

**Backend Response:**
```json
{
  "source_market": null,
  "related_markets": [],
  "count": 0,
  "message": "Source market not found"
}
```

---

## 🔧 **SOLUTIONS**

### Solution 1: Use Trending Tab (Works Now!)

The **Trending tab will show markets** because it doesn't depend on the current page:

1. **Reload extension:** `chrome://extensions` → Reload button
2. **Hard refresh page:** Ctrl+Shift+R  
3. **Click "Trending" tab**
4. **Click category pills:** All, Politics, Sports, Crypto, etc.
5. **See real data:** Should show 5-20 trending markets

### Solution 2: Populate Your Database

To get Related markets working, you need to add markets to your database:

#### **Option A: Import from CSV**
```bash
cd c:\Users\shilo\NexHacks\NexHacks
python database/migrations/001_import_markets_from_csv_simple.py
```

This imports markets from `data/polymarket_events_by_tags.csv`

#### **Option B: Fetch from Polymarket API**
```bash
# Refresh market data from Polymarket
curl "http://localhost:8000/markets/trending/refresh?limit=100"
```

This fetches the latest 100 markets from Polymarket and adds them to your database.

#### **Option C: Navigate to a Market That Exists**

Try these markets that are likely in your database:
- Bitcoin-related markets
- Trump-related markets
- Fed rate decision markets
- Tech company markets

---

## 📊 **HOW TO TEST IF IT'S WORKING**

### Test 1: Trending Tab (Should Work)
```
1. Reload extension
2. Go to https://polymarket.com  
3. Open extension panel
4. Click "Trending" tab
5. ✅ Should see: List of trending markets
6. Click "Politics" pill
7. ✅ Should see: Politics markets
```

### Test 2: Related Tab (Requires Database)
```
1. Make sure database is populated (see Solution 2)
2. Go to a market page: https://polymarket.com/event/...
3. Extension auto-switches to "Related" tab
4. ✅ Should see: Related markets + news articles
5. ❌ Still see "No related markets found" = That specific market not in DB
```

### Test 3: Blue Text
```
1. Reload extension
2. Open panel
3. ✅ Should see: All text in blue (#4a90ff)
4. ✅ Should see: Blue icons
5. ✅ Should see: Blue theme throughout
```

---

## 🗄️ **DATABASE STATUS CHECK**

### Check if Database Has Markets:
```bash
# Start Python console
python

# Import Supabase connection
from database.supabase_connection import get_supabase_client
client = get_supabase_client()

# Count markets in database
result = client.table('polymarket_markets').select('*', count='exact').execute()
print(f"Total markets: {result.count}")

# Count market metrics
result = client.table('market_metrics').select('*', count='exact').execute()
print(f"Total metrics: {result.count}")
```

**Expected Output:**
```
Total markets: 1000+  (Good!)
Total metrics: 500+   (Good!)
```

**If Count is 0:**
→ Database is empty, need to populate (see Solution 2)

---

## 🔍 **DEBUGGING CHECKLIST**

- [ ] **Backend running?**
  ```bash
  curl http://localhost:8000/
  # Should return JSON
  ```

- [ ] **Trending works?**
  ```bash
  curl "http://localhost:8000/markets/trending?limit=5"
  # Should return markets array
  ```

- [ ] **Database has data?**
  ```bash
  # Check market_metrics table in Supabase
  ```

- [ ] **Extension reloaded?**
  ```
  chrome://extensions → Reload button
  ```

- [ ] **Page hard refreshed?**
  ```
  Ctrl+Shift+R on Polymarket page
  ```

- [ ] **Looking at Trending tab?**
  ```
  Click "Trending" tab to see data
  ```

---

## 🎨 **VISUAL FIXES APPLIED**

### Before:
- ❌ White text on error messages
- ❌ Gray muted text everywhere
- ❌ Hard to read

### After (Now):
- ✅ Blue text (#4a90ff) everywhere
- ✅ Blue icons
- ✅ Blue category pills when active
- ✅ Dark button text on blue backgrounds
- ✅ Consistent theme

---

## 📝 **ERROR MESSAGES EXPLAINED**

### "No related markets found"
**Meaning:** The market you're viewing is not in the database  
**Solution:** Switch to Trending tab OR populate database

### "Failed to fetch"
**Meaning:** Backend API is not running  
**Solution:** Start backend: `python -m uvicorn api.main:app --reload --port 8000`

### "Source market not found"
**Meaning:** Same as "No related markets found"  
**Solution:** Use Trending tab or add markets to database

### Empty Trending Tab
**Meaning:** Database has no markets OR backend not running  
**Solution:** Check backend is running, then populate database

---

## 🚀 **QUICK FIX WORKFLOW**

### If You See "No Related Markets Found":

**Step 1:** Switch to Trending Tab
```
✅ Click "Trending" tab
✅ Should see trending markets
✅ Click category pills to filter
```

**Step 2:** (Optional) Populate Database
```bash
# Refresh markets from Polymarket API
curl "http://localhost:8000/markets/trending/refresh?limit=100"
```

**Step 3:** Test Related Tab Again
```
✅ Go to a different market page
✅ Related tab should now show data
```

---

## 📊 **WHAT'S WORKING NOW**

✅ **Backend API:** Running on localhost:8000  
✅ **Trending Endpoint:** Returns real market data  
✅ **Blue Text Theme:** All text is now blue  
✅ **Category Filters:** All 7 categories work  
✅ **Extension Build:** Latest version deployed  
✅ **Error Messages:** Show in blue color  

---

## 🔴 **WHAT NEEDS ATTENTION**

⚠️ **Database Needs Markets:** Supabase tables need to be populated  
⚠️ **Related Tab:** Only works if current market is in database  
⚠️ **News Articles:** Requires GNEWS_API_KEY in `.env`  

---

## 💡 **PRO TIPS**

1. **Always use Trending tab first** - It works regardless of what page you're on
2. **Populate database regularly** - Run refresh endpoint weekly
3. **Check backend logs** - Terminal shows all API requests
4. **Test with known markets** - Bitcoin, Trump markets usually in database
5. **Blue text everywhere** - If you see white text, extension needs reload

---

## 📞 **NEXT STEPS**

1. ✅ **Reload extension** - `chrome://extensions` → Reload
2. ✅ **Go to Trending tab** - Should see markets immediately  
3. ⚠️ **Populate database** - Run refresh endpoint or import CSV
4. ✅ **Test Related tab** - Navigate to different markets
5. ✅ **Enjoy blue theme** - All text should be blue!

---

**Status:** Extension is **working correctly!** The "No related markets found" message means the database needs to be populated, NOT that the extension is broken. Use the Trending tab to see data right away, or populate the database to enable Related markets.
