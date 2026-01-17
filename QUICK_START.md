# 🚀 Quick Start Guide

## In 60 Seconds

### Build & Load Extension
```bash
# From Extension directory
npm run build
# or
yarn build

# Then in Chrome:
# 1. Go to chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the Extension folder
```

### Test It
1. Navigate to any website
2. Click "Open panel" button (bottom-right)
3. See panel appear on right with:
   - ✅ Close button
   - ✅ Context header (sticky)
   - ✅ Market context
   - ✅ Ideas section
4. Refresh page
5. Panel position remembered ✅

### Check Console
```
[CONTENT] Panel opened
[CONTENT] Shadow DOM structure created
[CONTENT] UI initialization complete
```

---

## File Quick Reference

### For Context/News Data
**File**: `src/utils/contextData.ts`

```typescript
// To add more outlets:
export const MOCK_OUTLETS: Outlet[] = [
  {
    name: 'Your News',
    stance: 'Support', // or 'Neutral', 'Oppose'
    confidence: 80,     // 0-100
    rationale: 'Why this outlet supports...',
  },
  // ...
];

// To replace with API call:
// export async function getOutlets(slug: string) {
//   const response = await fetch(`/api/outlets/${slug}`);
//   return response.json();
// }
```

### For Panel Styling
**File**: `src/content/shadowStyles.ts`

```typescript
// All component styles here
// Safe from page CSS conflicts
// Add new .class-name { ... } as needed
```

### For Context Header Layout
**File**: `src/components/ContextHeader.tsx`

```typescript
// Sections:
// 1. Current Event (title, URL, slug)
// 2. Outlet Stance (4 outlets)
// 3. Key Voices (2 analysts)

// To modify colors:
// Support: '#4caf50' (green)
// Neutral: '#ff9800' (orange)
// Oppose: '#f44336' (red)
```

### For Layout Modes
**File**: `src/content/content.tsx`

```typescript
// Docked mode:
// - position: fixed; right: 16px; top: 16px; bottom: 16px
// - document.documentElement.style.paddingRight = "404px"

// Floating mode:
// - position: fixed; left: x; top: y; width: w; height: h
// - No page push
```

---

## Common Tasks

### Add a New Outlet
1. Open `src/utils/contextData.ts`
2. Add to `MOCK_OUTLETS` array:
```typescript
{
  name: 'TechNews Daily',
  stance: 'Support',
  confidence: 72,
  rationale: 'AI adoption catalyst remains strong...',
}
```
3. Rebuild and reload

### Change Default Width
1. Open `src/utils/storage.ts`
2. Find: `const DEFAULT_PANEL_WIDTH = 380`
3. Change to desired value

### Switch Layout Mode
1. Open DevTools Console
2. Run:
```javascript
chrome.storage.sync.get('overlay_state', (data) => {
  data.overlay_state.layoutMode = 'floating'; // or 'docked'
  chrome.storage.sync.set(data);
});
```
3. Reload extension

### Add API Integration
1. In `contextData.ts`, replace mock data:
```typescript
export async function getContextualOutlets(slug: string): Promise<Outlet[]> {
  try {
    const response = await fetch(`https://api.example.com/outlets/${slug}`);
    return response.json();
  } catch (error) {
    console.error('API error:', error);
    return MOCK_OUTLETS; // Fallback to mock
  }
}
```

2. Update `ContextHeader.tsx` to await:
```typescript
const [outlets, setOutlets] = useState<Outlet[]>([]);

useEffect(() => {
  getContextualOutlets(context.slug).then(setOutlets);
}, [context.slug]);
```

---

## File Dependencies

### Direct Imports
```
content.tsx
├─ FloatingAssistant.tsx
│  └─ ContextHeader.tsx
│     └─ contextData.ts
├─ overlayStore.ts
│  └─ storage.ts
└─ shadowStyles.ts
```

### No External Dependencies
- ✅ No axios, fetch wrapper
- ✅ No moment.js, date library
- ✅ No UI framework beyond React
- ✅ Pure Chrome API usage

---

## Debugging Checklist

### Panel Won't Open
- [ ] Check storage: `chrome.storage.sync.get('overlay_state', console.log)`
- [ ] Check console for errors
- [ ] Hard refresh (Ctrl+Shift+R)
- [ ] Rebuild extension

### Page Not Pushed
- [ ] Check: `document.documentElement.style.paddingRight`
- [ ] Verify: `state.layoutMode === 'docked'`
- [ ] Verify: `state.open === true`

### Context Header Empty
- [ ] Check: ContextHeader is rendering
- [ ] Check: contextData.ts utilities work
- [ ] Verify: No console errors

### Drag Not Working
- [ ] Verify: `state.layoutMode === 'floating'`
- [ ] Check: Drag start in header area
- [ ] Check: Not clicking action buttons

---

## Key Constants

```typescript
// Size defaults (storage.ts)
DEFAULT_PANEL_WIDTH = 380
DEFAULT_PANEL_HEIGHT = 720
MIN_PANEL_WIDTH = 280
MAX_PANEL_WIDTH = 560

// Position defaults
DEFAULT_X = 16
DEFAULT_Y = 16

// Storage debounce (overlayStore.ts)
DEBOUNCE_TIMER = 500 // ms

// Z-index stack
Panel container: 2147483647
Shadow host: 2147483647
ContextHeader: 10
```

---

## Performance Tips

1. **Reduce re-renders**: Memoize ContextHeader components
2. **Cache data**: Store API results locally
3. **Lazy load**: Only fetch when panel opens
4. **Compress storage**: Use minimal state shape

---

## Testing Examples

### Test Page Push
```javascript
// Should be "404px"
document.documentElement.style.paddingRight
```

### Test Storage Persistence
```javascript
// Open panel, change x position, refresh page
chrome.storage.sync.get('overlay_state', console.log)
// Should show same position
```

### Test Drag Limits
```javascript
// Drag panel to edge
// Should stop at viewport boundary
// Verify panelEl.style.left/top don't exceed bounds
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Multiple shadow roots" | Reload issue | Hard refresh (Ctrl+Shift+R) |
| "Panel position wrong" | Storage corruption | Clear extension storage |
| "Context header blank" | API not called | Check console errors |
| "Drag not working" | Wrong layout mode | Verify layoutMode: 'floating' |
| "Page not pushed" | State not updated | Check render() function called |

---

## Resources

### Documentation
- `IMPLEMENTATION_SUMMARY.md` - What was done
- `ARCHITECTURE.md` - System design
- `TESTING_GUIDE.md` - How to test
- `FILE_CHANGES_DETAIL.md` - Code changes

### Code Files
- `contextData.ts` - Mock data
- `ContextHeader.tsx` - Display component
- `content.tsx` - Panel management
- `overlayStore.ts` - State management

### Standards
- TypeScript strict mode ✅
- Chrome Web API v3 ✅
- React 18+ patterns ✅
- Shadow DOM best practices ✅

---

## Next Steps

### For Development
1. Set up hot reload (Webpack watch)
2. Add unit tests for utilities
3. Add E2E tests for flow
4. Integrate real API

### For Production
1. User testing feedback
2. Performance optimization
3. Error monitoring
4. Analytics integration

---

## Questions?

Refer to:
1. Code comments (inline documentation)
2. Type definitions (self-documenting)
3. ARCHITECTURE.md (system flow)
4. Test cases in TESTING_GUIDE.md

---

**Status**: ✅ Ready to use  
**Last Updated**: January 17, 2026  
**Support**: Full documentation provided  

Good luck! 🚀
