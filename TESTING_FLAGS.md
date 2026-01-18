# API Integration Testing Flags

**Status**: Implementation complete. All assumptions flagged for testing below.

**Date**: January 17, 2026  
**Modified Files**: 6  
**New Files**: 1  
**Lines Added**: ~280

---

## 🚨 Critical Testing Flags (MUST TEST BEFORE PRODUCTION)

### FLAG #1: Backend URL Configuration
**File**: `Extension/src/utils/api.ts` (lines 4-11)  
**Assumption**: Backend runs on `http://localhost:8000` or environment variable `VITE_BACKEND`/`VITE_BACKEND_URL`  
**Confidence**: 85%  
**Action Required**:
- [ ] Verify backend URL is correct for your environment
- [ ] Check if CORS is enabled on backend
- [ ] Update Vite env vars if needed (`.env.development`, `.env.production`)

**Test Command**:
```bash
# Check backend availability
curl http://localhost:8000/docs

# Test from extension context
# Open extension console and check [API] logs
```

---

### FLAG #2: API Response Shape
**File**: `Extension/src/utils/api.ts` (line 7)  
**Assumption**: API returns `{ amplify: MarketRecommendation[], hedge: MarketRecommendation[] }`  
**Confidence**: 80% (untested against actual backend)  
**Action Required**:
- [ ] Run test fetch and verify response structure
- [ ] Check if fields match `MarketRecommendation` interface
- [ ] Validate score values are between 0-1 (for % display)

**Test Steps**:
1. Navigate to Polymarket
2. Open Extension console (DevTools → Elements → + → [extension] iframe)
3. Run: `curl -X POST http://localhost:8000/v1/recommendations -H "Content-Type: application/json" -d '{...}'`
4. Check response matches expected shape

**Expected Response**:
```json
{
  "amplify": [
    {"id": "...", "title": "...", "url": "...", "category": "...", "score": 0.85, "reason": "..."},
    ...
  ],
  "hedge": [...]
}
```

---

### FLAG #3: CORS and Fetch Behavior
**File**: `Extension/src/utils/api.ts` (line 24-35)  
**Assumption**: Direct fetch works due to CORS being enabled on backend  
**Confidence**: 85%  
**Action Required**:
- [ ] Test for CORS errors in DevTools console
- [ ] If CORS fails, implement chrome.runtime.sendMessage bridge
- [ ] Verify Content Security Policy doesn't block fetch

**Expected Behavior**: No CORS errors in console

**Fallback Implementation**: If CORS fails, switch to message passing:
```typescript
// TODO: Implement this if CORS errors occur
const response = await new Promise((resolve, reject) => {
  chrome.runtime.sendMessage({ type: 'FETCH_RECOMMENDATIONS', request }, (response) => {
    if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
    else resolve(response);
  });
});
```

---

### FLAG #4: API Timeout Configuration
**File**: `Extension/src/utils/api.ts` (line 14)  
**Assumption**: 5 second timeout is appropriate for API response  
**Confidence**: 75%  
**Action Required**:
- [ ] Measure actual API response time
- [ ] If slow, increase timeout to 7-10s
- [ ] If fast, reduce to 3-4s to detect faster failures

**Test Method**:
1. Open Extension console
2. Watch logs: `[API] Fetching recommendations...` and `[API] Recommendations received:`
3. Note time difference
4. Adjust if needed: `const API_TIMEOUT_MS = 7000;`

---

### FLAG #5: Error Handling Strategy
**File**: `Extension/src/utils/api.ts` (line 50-54)  
**Assumption**: Errors throw, parent handles gracefully with SAMPLE_MARKETS fallback  
**Confidence**: 90%  
**Action Required**:
- [ ] Trigger network error and verify extension doesn't crash
- [ ] Verify DirectionalIdeas shows SAMPLE_MARKETS on error
- [ ] Check console logs show error clearly

**Test Steps**:
1. Pause backend (`docker stop <backend-container>`)
2. Navigate to Polymarket market
3. Watch for error in console: `[FloatingAssistant] Failed to fetch recommendations:`
4. Verify DirectionalIdeas still shows (with SAMPLE_MARKETS)
5. Resume backend

---

## 🔍 Implementation Flags (Test During Development)

### FLAG #6: Topic/Entity Keyword Matching
**File**: `Extension/src/utils/localProfile.ts` (lines 9-29)  
**Assumption**: Simple keyword matching covers actual Polymarket titles  
**Confidence**: 70% (may need refinement)  
**Action Required**:
- [ ] Test against 50+ real market titles
- [ ] Identify missing keywords and add them
- [ ] Consider case-sensitivity (already handled with `.toLowerCase()`)

**Test Steps**:
1. Open Extension console
2. Watch logs: `[LocalProfile] Built profile:` shows `topicCount` and `entityCount`
3. Navigate different markets and verify keywords are matched
4. If keywords missing, add to TOPIC_KEYWORDS or ENTITY_KEYWORDS objects

**Refinement**: If keyword matching insufficient, consider:
- NLP-based topic extraction
- ML model for entity recognition
- API-based topic detection

---

### FLAG #7: Recent Interactions Window
**File**: `Extension/src/utils/localProfile.ts` (line 32)  
**Assumption**: Last 50 market interactions is appropriate (≈30 days of usage)  
**Confidence**: 75%  
**Action Required**:
- [ ] Monitor if 50 is too large/small for meaningful recommendations
- [ ] Adjust window size if needed
- [ ] Consider time-based window (e.g., last 7 days) instead

**Test Steps**:
1. Build local profile in console: 
   ```javascript
   const storage = await chrome.storage.local.get('market_history');
   console.log('History size:', storage.market_history.length);
   ```
2. If >500 items and only using 50, may need larger window
3. If <20 items, current window is fine

---

### FLAG #8: Empty Profile Fallback
**File**: `Extension/src/utils/localProfile.ts` (line 100)  
**Assumption**: API handles empty topic/entity counts gracefully  
**Confidence**: 85%  
**Action Required**:
- [ ] Test with fresh user (no market history)
- [ ] Verify API doesn't error on empty profiles
- [ ] Check if recommendations still generate with empty local_profile

**Test Steps**:
1. Clear storage: `chrome.storage.local.clear()`
2. Navigate to new market
3. Verify no errors in console
4. Check if recommendations still appear

---

### FLAG #9: API Recommendations Props Flow
**File**: `Extension/src/components/DirectionalIdeas.tsx` (lines 5-13)  
**Assumption**: Parent properly populates `yesList`, `noList`, `loading` props  
**Confidence**: 95% (implementation straightforward)  
**Action Required**:
- [ ] Verify props are passed correctly
- [ ] Check loading spinner appears during fetch
- [ ] Verify recommendations display when API returns data

**Test Steps**:
1. Add breakpoint in DirectionalIdeas render
2. Check props: `console.log({ yesList, noList, loading })`
3. Verify prop values match API response and loading state

---

### FLAG #10: Market Change Detection
**File**: `Extension/src/components/FloatingAssistant.tsx` (lines 192-223)  
**Assumption**: Fetch triggers only on `currentMarket.url` change  
**Confidence**: 90%  
**Action Required**:
- [ ] Test rapid market navigation doesn't cause duplicate fetches
- [ ] Verify debouncing not needed
- [ ] Monitor API call count in console logs

**Test Steps**:
1. Navigate between different markets quickly
2. Watch console for `[FloatingAssistant] Fetching recommendations for:` messages
3. Count API calls - should match market changes (not more)
4. If duplicate calls, add debouncing:
   ```typescript
   useEffect(() => {
     const timer = setTimeout(() => {
       // ... fetch logic
     }, 300); // 300ms debounce
     return () => clearTimeout(timer);
   }, [currentMarket.url]);
   ```

---

## ✅ Verification Checklist

### Pre-Testing Setup
- [ ] Backend is running on correct URL
- [ ] Extension is loaded in Chrome
- [ ] DevTools is open to Extension console
- [ ] Test user has market history (or cleared cache for fresh start)

### Functional Testing
- [ ] Navigate to Polymarket.com
- [ ] Panel opens with DirectionalIdeas
- [ ] Console shows `[FloatingAssistant] Fetching recommendations for: ...`
- [ ] Within 5 seconds, recommendations appear
- [ ] Recommendations are from API (not SAMPLE_MARKETS)
- [ ] "Add to basket" and "Open" buttons work
- [ ] Navigate different market → recommendations update

### Error Testing
- [ ] Stop backend → error logged, SAMPLE_MARKETS shown
- [ ] Clear market history → API handles empty profile
- [ ] CORS error → check if chrome.runtime.sendMessage bridge needed
- [ ] Timeout → verify 5s timeout triggers (slow API)

### Performance Testing
- [ ] API response time < 5s
- [ ] No duplicate API calls on rapid navigation
- [ ] Extension remains responsive during fetch
- [ ] Memory usage doesn't spike with recommendations loaded

### Browser Console Checks
- [ ] No TypeScript errors
- [ ] No network CORS errors
- [ ] All `[API]`, `[FloatingAssistant]`, `[DirectionalIdeas]`, `[LocalProfile]` logs appear
- [ ] No unhandled promise rejections

---

## 📋 Known Uncertainties to Track

| Uncertainty | File | Confidence | Impact | Resolution |
|------------|------|-----------|--------|-----------|
| API response shape | api.ts | 80% | Medium | Run actual API test |
| CORS working | api.ts | 85% | High | Check browser console |
| Keyword matching complete | localProfile.ts | 70% | Low | Monitor in production |
| Timeout appropriate | api.ts | 75% | Low | Measure response time |
| Empty profile handling | localProfile.ts | 85% | Medium | Test fresh user |
| Entity extraction method | localProfile.ts | 70% | Low | Improve if needed |
| Loading spinner CSS | DirectionalIdeas.tsx | 95% | Low | CSS may need tweaks |
| Debouncing needed | FloatingAssistant.tsx | 90% | Low | Monitor call count |
| Backend URL env vars | api.ts | 85% | High | Document setup |
| Type compatibility | types/index.ts | 95% | Medium | TypeScript compile check |

---

## 🔧 Quick Troubleshooting

### "Failed to fetch recommendations" Error
1. Check backend is running: `curl http://localhost:8000/docs`
2. Check CORS headers: Open Network tab, inspect response headers
3. Check Content: `Content-Type: application/json`
4. Check request body in Network tab

### SAMPLE_MARKETS Still Showing (Expected on Error)
1. This is correct behavior - graceful fallback
2. Check console for actual error message
3. Verify backend API response format

### Loading Spinner Stuck
1. Check API timeout (should show error after 5s)
2. Check Network tab for pending requests
3. Consider increasing timeout

### Recommendations Don't Update on New Market
1. Check `currentMarket.url` is different
2. Check console for `[FloatingAssistant] Fetching recommendations for:` message
3. Check if useEffect dependency array includes `currentMarket.url`

---

## 📝 Post-Testing Documentation

After testing, update:
1. **Backend URL**: Update if different from localhost:8000
2. **Timeout value**: Adjust if average response time differs
3. **Keyword lists**: Add missing topics/entities found in production
4. **Local profile window**: Adjust if 50 interactions too large/small

---

## 🎯 Success Criteria

✅ **Implementation is successful when**:
1. Real recommendations display in DirectionalIdeas
2. Recommendations change when navigating to different markets
3. No console errors (TypeScript, network, unhandled promises)
4. Error handling works (shows SAMPLE_MARKETS gracefully)
5. All flags documented above have been tested
6. Response time < 5 seconds consistently
7. No duplicate API calls on rapid navigation
8. Empty user profile doesn't cause errors

---

## 📌 Related Files

- **Implementation Files**:
  - [Extension/src/utils/api.ts](Extension/src/utils/api.ts) - API fetch wrapper
  - [Extension/src/utils/localProfile.ts](Extension/src/utils/localProfile.ts) - Profile builder
  - [Extension/src/types/index.ts](Extension/src/types/index.ts) - Type definitions
  - [Extension/src/components/FloatingAssistant.tsx](Extension/src/components/FloatingAssistant.tsx) - Main component
  - [Extension/src/components/DirectionalIdeas.tsx](Extension/src/components/DirectionalIdeas.tsx) - Recommendations display

- **Backend Files**:
  - `backend/routers/recommendations.py` - API endpoint
  - `backend/services/recommendation_engine.py` - Recommendation logic

- **Configuration Files**:
  - `.env.development` - Environment variables
  - `.env.production` - Production environment variables

---

*Last updated*: January 17, 2026  
*Implementation version*: 1.0  
*Status*: Ready for testing
