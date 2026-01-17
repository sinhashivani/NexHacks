# Quick Reference: Layout Redesign

## What Changed

### 1️⃣ **Data Model** (`contextData.ts`)
```typescript
// Added to Outlet interface:
url: string;  // e.g., "https://wsj.com"
```

### 2️⃣ **Outlet Display** (`ContextHeader.tsx`)
| Before | After |
|--------|-------|
| Large stacked cards | Compact grid boxes |
| ~8px padding, 6px gap | ~6px padding, 6px gap |
| 4 outlets shown | 6 outlets shown |
| Non-interactive | Fully clickable |
| No hover effects | Hover brightens + lifts |
| No tooltip | Tooltip on hover (URL) |
| No click action | Opens URL in new tab |

### 3️⃣ **Layout Modes** (`FloatingAssistant.tsx`)
| Scenario | Layout |
|----------|--------|
| Docked, width ≥600px | **Two-column** (30/70) |
| Docked, width <600px | **Single-column** |
| Floating, any width | **Single-column** |

### 4️⃣ **URL Handling** (`background.ts`)
```javascript
// New handler in background service worker
chrome.runtime.onMessage.addListener((request) => {
  if (request.action === 'openUrl') {
    // Validate + open safely
    chrome.tabs.create({ url, active: false });
  }
});
```

---

## Testing Quick-Start

### Visual Test
```
1. Open Polymarket in Chrome
2. Load extension (npm run build → Load unpacked)
3. Panel should appear on right side
4. Look for:
   ✓ Compact "Current Event" (2 lines)
   ✓ 6 outlet boxes in grid (color-coded)
   ✓ Key Voices below
```

### Hover Test
```
1. Hover over any source box (WSJ, Bloomberg, etc)
2. Should see:
   ✓ Box gets brighter
   ✓ Lifts up slightly
   ✓ Colored shadow appears
   ✓ Cursor becomes pointer
   ✓ URL shows in browser tooltip
```

### Click Test
```
1. Click any source box
2. Should:
   ✓ Open URL in new background tab
   ✓ NOT block current page
   ✓ Show no console errors
```

### Two-Column Test (Docked Mode)
```
1. Resize panel wider than 600px
2. Should see:
   ✓ Left column (30%): Context header
   ✓ Right column (70%): Similar Trades
   ✓ Vertical separator line
3. Scroll left column independently
4. Scroll right column independently
5. Both should work without affecting other
```

### Responsive Test
```
1. Resize panel narrower than 600px
2. Should switch to single-column
3. Resize back wider than 600px
4. Should switch back to two-column
5. No jumping or visual glitches
```

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Source boxes | 6 total |
| Key voices shown | 2 analysts |
| Two-column breakpoint | 600px width |
| Left column width | 30% |
| Right column width | 70% |
| Source box min-width | 70px |
| Grid gap | 6px |
| Hover lift animation | 2px up |

---

## Color Palette

```
Support   → #4caf50 (Green)
Oppose    → #f44336 (Red)  
Neutral   → #ff9800 (Orange)

Text      → rgba(255,255,255)
Background → rgba(15,15,18,0.95)
Hover     → rgba(255,255,255,0.12)
Border    → rgba(255,255,255,0.08)
```

---

## Files Modified

```
Extension/
├── src/
│   ├── utils/
│   │   └── contextData.ts          [+url field to outlets]
│   ├── components/
│   │   ├── ContextHeader.tsx       [Redesigned layout]
│   │   └── FloatingAssistant.tsx   [Two-column logic]
│   └── background/
│       └── background.ts            [URL opener handler]
```

---

## Build & Test

```bash
# Build
npm run build

# Load in Chrome
# 1. chrome://extensions
# 2. Enable Developer Mode
# 3. Load unpacked → Extension/

# Check for errors
# DevTools Console → Should show [CONTEXT] logs
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Outlet boxes tiny | Grid too wide | Check width breakpoint (≥600px) |
| URLs don't open | Popup blocked | Check background.ts handler logs |
| Two-column missing | Width <600px | Widen panel to ≥600px |
| Similar Trades small | Single-column | Switch to docked mode, width ≥600px |
| Hover effects missing | CSS issue | Check ContextHeader inline styles |
| Layout jumping | Responsive | Check breakpoint at 600px |

---

## Before vs After Comparison

### ContextHeader Size
- **Before**: ~450px height (4 tall outlet cards + analysts)
- **After**: ~120px height (compact boxes + condensed sections)
- **Result**: 75% reduction in vertical space ✅

### Similar Trades Space
- **Before**: 20-30% of panel
- **After**: 70% of panel (two-column) or full-width (single-column)
- **Result**: 3x more space ✅

### Outlet Visibility
- **Before**: 4 outlets shown
- **After**: 6 outlets shown in grid
- **Result**: 50% more outlets visible ✅

### Interactivity
- **Before**: View-only
- **After**: Clickable boxes → Open URL
- **Result**: Direct source access ✅

---

## Next Steps

1. [ ] Build extension (`npm run build`)
2. [ ] Load in Chrome (chrome://extensions)
3. [ ] Run visual tests (see above)
4. [ ] Test hover on source boxes
5. [ ] Test click to open URLs
6. [ ] Test two-column layout at 600px width
7. [ ] Test responsive shrink/grow
8. [ ] Check console for errors

All tests passing? ✅ You're ready to integrate with real data!

---

## Support

- **Visual guide**: See `LAYOUT_VISUAL_GUIDE.md`
- **Detailed changes**: See `LAYOUT_REDESIGN_SUMMARY.md`
- **Code review**: Check file changes in source
- **Errors?**: Run `npm run build` and check output

---

**Status**: ✅ READY TO BUILD

🚀 Ready to see the new layout? Build it now!

```bash
npm run build
```
