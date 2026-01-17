# Visual Layout Guide

## Before vs After

### BEFORE: Single Column, Tall Outlet Section
```
┌────────────────────────────────────┐
│      Trade Assistant        [✕]    │ ← Header (fixed)
├────────────────────────────────────┤
│ CURRENT EVENT                      │ ← Big block
│ "Will Bitcoin reach $100k..."      │
│ https://polymarket.com/market...   │
├────────────────────────────────────┤
│ OUTLET STANCE                      │ ← Tall stacked cards
│ ┌──────────────────────────────┐   │
│ │ WSJ              Support 85% │   │
│ │ Recent analysis aligns...    │   │
│ │ Confidence: 85%              │   │
│ └──────────────────────────────┘   │
│ ┌──────────────────────────────┐   │
│ │ Bloomberg        Support 78% │   │
│ │ Market momentum indicators.. │   │
│ │ Confidence: 78%              │   │
│ └──────────────────────────────┘   │
│ ┌──────────────────────────────┐   │
│ │ Reuters           Neutral 65% │  │
│ │ Mixed signals from...        │   │
│ │ Confidence: 65%              │   │
│ └──────────────────────────────┘   │
│ ┌──────────────────────────────┐   │
│ │ FT               Neutral 72%  │  │
│ │ Consensus suggests...        │   │
│ │ Confidence: 72%              │   │
│ └──────────────────────────────┘   │
├────────────────────────────────────┤
│ KEY VOICES                         │ ← Limited space
│ [2 analyst cards]                  │
├────────────────────────────────────┤
│ Similar Trades                     │ ← Only 20-30% space
│ If you like YES (Buy)              │
│ - Bitcoin at $100k... (85%)        │
│ - Crypto regulatory... (72%)       │
│ [Need to scroll more]              │
│                                    │
└────────────────────────────────────┘
```

**Problem**: Takes up 50%+ space just for outlets, constrains Similar Trades

---

### AFTER: Compact Headers + Two-Column (Wide) / Single-Column (Narrow)

#### A) Docked Mode with Width ≥ 600px (TWO-COLUMN)
```
┌──────────────────────────────────────────────────────────┐
│      Trade Assistant                              [✕]    │ ← Fixed header
├──────────────────────────────────────────────────────────┤
│                                                           │
│  LEFT 30%           │  RIGHT 70%                         │
│  ┌────────────────┐ │  ┌──────────────────────────────┐  │
│  │ CURRENT EVENT  │ │  │   SIMILAR TRADES             │  │
│  │ (2-line title) │ │  │ (SCROLLABLE - MAIN FOCUS)    │  │
│  │ (1-line URL)   │ │  │                              │  │
│  │                │ │  │ If you like YES (Buy)        │  │
│  │ SOURCES        │ │  │ ┌──────────────────────────┐ │  │
│  │ ┌──┐┌──┐┌──┐   │ │  │ │ Bitcoin $100k?    85%    │ │  │
│  │ │WS││BB││RT│   │ │  │ │ Similar YES exposure     │ │  │
│  │ │J ││G ││R │   │ │  │ │ [Open] [Add to basket]   │ │  │
│  │ │✓ ││✓ ││~│   │ │  │ └──────────────────────────┘ │  │
│  │ │85││78││65│   │ │  │ ┌──────────────────────────┐ │  │
│  │ └──┘└──┘└──┘   │ │  │ │ GDP Growth 2%?    72%    │ │  │
│  │ ┌──┐┌──┐┌──┐   │ │  │ │ Complements YES profile  │ │  │
│  │ │FT││CB││EC│   │ │  │ │ [Open] [Add to basket]   │ │  │
│  │ │~ ││✗ ││✗ │   │ │  │ └──────────────────────────┘ │  │
│  │ │72││68││75│   │ │  │ ┌──────────────────────────┐ │  │
│  │ └──┘└──┘└──┘   │ │  │ │ Fed Rate Cut Q2?  80%    │ │  │
│  │ [scrollable]   │ │  │ │ Curve inversion signal   │ │  │
│  │                │ │  │ │ [Open] [Add to basket]   │ │  │
│  │ KEY VOICES     │ │  │ └──────────────────────────┘ │  │
│  │ [2 analysts]   │ │  │ [... more trades below ...]  │  │
│  │                │ │  │                              │  │
│  │[scroll area]   │ │  │ If you like NO (Sell)        │  │
│  │                │ │  │ ┌──────────────────────────┐ │  │
│  └────────────────┘ │  │ │ Inflation stays 3%? 70% │ │  │
│                     │  │ │ Bearish headwinds      │ │  │
│                     │  │ │ [Open] [Add to basket] │ │  │
│                     │  │ └──────────────────────┘ │  │
│                     │  │ [... more trades ...]    │  │
│                     │  │[scrollable independently]│  │
│                     │  └──────────────────────────┘  │
│                     │                                 │
└──────────────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Context header (left) always visible while scrolling trades
- ✅ Similar trades get ~70% of panel width
- ✅ Compact outlet boxes (6 visible) with hover tooltips
- ✅ Left and right columns independently scrollable

---

#### B) Docked Mode with Width < 600px OR Floating Mode (SINGLE-COLUMN)
```
┌─────────────────────────────────┐
│  Trade Assistant          [✕]   │ ← Header
├─────────────────────────────────┤
│ CURRENT EVENT                   │ ← Compact (2-line title)
│ "Will Bitcoin..."               │
│ polymarket.com/...              │
├─────────────────────────────────┤
│ SOURCES (grid, responsive)      │ ← 6 outlets in compact boxes
│ ┌──┐ ┌──┐ ┌──┐                  │
│ │WS│ │BB│ │RT│                  │
│ │J │ │G │ │R │                  │
│ │✓ │ │✓ │ │~ │                  │
│ │85│ │78│ │65│                  │
│ └──┘ └──┘ └──┘                  │
│ ┌──┐ ┌──┐ ┌──┐                  │
│ │FT│ │CB│ │EC│                  │
│ │~ │ │✗ │ │✗ │                  │
│ │72│ │68│ │75│                  │
│ └──┘ └──┘ └──┘                  │
├─────────────────────────────────┤
│ KEY VOICES                      │ ← Compressed
│ A. Chen (Macro Analyst)         │
│ "Fed policy pivot creates..."   │
│ M. Rivera (Rates Trader)        │
│ "Curve inversion signals..."    │
├─────────────────────────────────┤
│ Similar Trades                  │ ← Gets majority of remaining space
│ If you like YES (Buy)           │
│ ┌─────────────────────────────┐ │
│ │ Bitcoin $100k?         85%  │ │
│ │ Similar YES exposure        │ │
│ │ [Open] [Add to basket]      │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ GDP Growth 2%          72%  │ │
│ │ Complements YES profile     │ │
│ │ [Open] [Add to basket]      │ │
│ └─────────────────────────────┘ │
│ [scrollable]                    │
│                                 │
└─────────────────────────────────┘
```

---

## Hover States on Source Boxes

### Normal State
```
┌──┐
│WS│  ← Border color: green (#4caf50)
│J │  ← Background: rgba(255,255,255,0.06)
│✓ │  ← Stance icon
│85│  ← Confidence %
└──┘
```

### Hover State
```
┌──┐
│WS│  ← Border: green, stays
│J │  ← Background: rgba(255,255,255,0.12) [brightens]
│✓ │  ← Lifted up 2px (translateY(-2px))
│85│  ← Box-shadow: green glow
└──┘    ← Cursor: pointer
        ← Tooltip shows: "https://wsj.com"
```

### Click
```
→ Opens https://wsj.com in new background tab
→ Uses chrome.runtime.sendMessage for safe opening
→ URL validated (http/https only)
→ No popup blockers
```

---

## Stance Colors Reference

| Stance | Color | RGB | Hex |
|--------|-------|-----|-----|
| Support | 🟢 Green | rgb(76, 175, 80) | #4caf50 |
| Oppose | 🔴 Red | rgb(244, 67, 54) | #f44336 |
| Neutral | 🟠 Orange | rgb(255, 152, 0) | #ff9800 |

Applied as:
- **Border color** on source boxes
- **Text color** for stance label
- **Box-shadow** on hover

---

## Layout Breakpoints

| Mode | Width | Layout |
|------|-------|--------|
| Docked | ≥600px | **Two-column** (30/70) |
| Docked | <600px | **Single-column** |
| Floating | Any | **Single-column** |

Two-column layout automatically activates when:
```javascript
state.layoutMode === 'docked' && state.width >= 600px
```

---

## Responsive Grid for Source Boxes

```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
gap: 6px;
```

**Result:**
- Each box: 70px minimum width
- Wraps to multiple rows automatically
- Fills available space with equal-width columns
- 6 outlets shown: 3 per row (on 240px+ width) → 2-3 rows

Example at different widths:
```
240px wide: 3 columns
┌──┐┌──┐┌──┐
│WS││BB││RT│
└──┘└──┘└──┘
┌──┐┌──┐┌──┐
│FT││CB││EC│
└──┘└──┘└──┘

180px wide: 2 columns  
┌──┐┌──┐
│WS││BB│
└──┘└──┘
┌──┐┌──┐
│RT││FT│
└──┘└──┘
┌──┐┌──┐
│CB││EC│
└──┘└──┘

120px wide: 1 column
┌──┐
│WS│
└──┘
┌──┐
│BB│
└──┘
...
```

---

## Space Allocation (Two-Column Mode)

```
Total width: 800px (example)
├─ Left column (30%): 240px
│  ├─ Current Event: ~40px height
│  ├─ Sources grid: ~80px height (2 rows × 40px)
│  └─ Key Voices: ~100px height
│  └─ Scroll area: ~240px height
│
└─ Right column (70%): 560px
   ├─ Header: ~50px
   ├─ YES ideas: ~200px
   ├─ NO ideas: ~200px
   └─ Scroll area: ~500px visible, unlimited scrollable

```

**Result**: Similar Trades section gets ~70% horizontal space + full independent scrolling

---

## No More Layout Jank

✅ **Before**: Viewport-width changes caused UI reflow
✅ **After**: Responsive breakpoint (600px) handles gracefully
✅ **Smooth transitions**: CSS transforms (no layout recalc)
✅ **Independent scrolling**: Both columns scroll without affecting other
✅ **Fixed header**: Always visible while scrolling content

---

## Implementation Files

Modified:
1. ✅ `src/utils/contextData.ts` - Added URLs
2. ✅ `src/components/ContextHeader.tsx` - Redesigned layout
3. ✅ `src/components/FloatingAssistant.tsx` - Two-column logic
4. ✅ `src/background/background.ts` - Safe URL opening

No changes to:
- DirectionalIdeas.tsx (content unchanged)
- FloatingAssistant.css (still valid)
- Content script positioning logic

---

**Status**: ✅ Ready to build and test

```bash
npm run build
```

Then load in Chrome and test the new layouts!
