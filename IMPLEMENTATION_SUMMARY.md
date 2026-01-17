# Implementation Summary: Docked/Floating Layout + Context Header

## Overview
Added a comprehensive context system with dual layout modes (docked sidebar + floating panel) and a rich context header showing market info, outlet stances, and analyst quotes.

## Files Created

### 1. `src/utils/contextData.ts`
**Purpose**: Mock data and utilities for context information

**Key Features:**
- `MOCK_OUTLETS`: 6 news outlets (WSJ, Bloomberg, Reuters, FT, CNBC, Economist) with stance, confidence, and rationale
- `MOCK_ANALYSTS`: 4 analyst profiles (Macro, Rates, Crypto, Tech) with quotes
- `extractSlug()`: Extract market identifier from URL/title
- `getContextualOutlets()`: Returns outlets sorted by confidence
- `getContextualAnalysts()`: Returns analyst list
- `getPageContext()`: Builds context from document.title and location

### 2. `src/components/PageContext.tsx`
**Purpose**: Displays current event/market information

**Rendered as**: Section header showing title, URL, and extracted slug

### 3. Updated `src/components/ContextHeader.tsx`
**Purpose**: Rich context header with outlets and analysts

**Sections:**
1. **Current Event**: Title, URL, slug from page
2. **Outlet Stance**: Top 4 outlets with stance (Support/Neutral/Oppose), confidence %, and rationale
3. **Key Voices**: Top 2 analysts with role and quote

**Styling**: Inline styles, dark theme, sticky positioning at top with zIndex: 10

## Files Modified

### 1. `src/types/index.ts`
**Change**: Added `layoutMode` to `OverlayState`
```typescript
export interface OverlayState {
  open: boolean;
  width: number;
  height: number;
  x: number;
  y: number;
  layoutMode: 'docked' | 'floating';
}
```

### 2. `src/utils/storage.ts`
**Changes**:
- Updated `getOverlayState()` to include `layoutMode: 'docked'` in default state
- Removed `minimized` field from default state (no longer used)
- Ensures backward compatibility with persisted state

### 3. `src/content/content.tsx`
**Major Changes**:

**Page Push System:**
- `applyPagePush(state)`: When docked mode is active and panel is open, sets `document.documentElement.style.paddingRight` to push page content
- Removes padding when panel closes or layout changes

**Panel Positioning:**
- `updatePanelPosition(state)`: Smart positioning logic
  - **Docked**: `position: fixed; right: 16px; top: 16px; bottom: 16px; width: state.width`
  - **Floating**: `position: fixed; left/top from state.x/y; width/height from state`

**Panel Element:**
- Changed from `position: absolute` to `position: fixed` for consistent viewport-relative positioning
- Properly handles both layout modes

### 4. `src/components/FloatingAssistant.tsx`
**Major Changes**:

**Layout Mode Awareness:**
- Drag/resize handlers now check `state.layoutMode !== 'floating'` to disable in docked mode
- Resize handle only renders in floating mode (`showResizeHandle` variable)
- Header cursor changes based on layout mode

**Height Behavior:**
- Docked mode: `height: auto` (expands to fit content)
- Floating mode: `height: state.height` (fixed height)

**Removed Old Context:**
- Removed `mockSignals` import from ContextHeader
- ContextHeader now manages its own data

## State Management

### `overlayStore.ts` (unchanged but compatible)
- Debounced persistence at 500ms intervals
- Only persists `{open, x, y, width, height, layoutMode}`
- Immediate UI update, debounced storage write

## Layout Modes

### Docked Mode (Default)
- Panel fixed to right side: `right: 16px; top: 16px; bottom: 16px`
- Width: 380px (default)
- Page content pushed left by: `width + 24px` padding
- Drag disabled (header non-interactive)
- Resize handle hidden
- Height: auto (fills available vertical space)

### Floating Mode
- Panel positioned at `x, y` from state
- Width/height customizable
- Draggable header (cursor: grab/grabbing)
- Resizable from bottom-right corner
- No page push applied
- Fixed dimensions

## Visual Flow

```
┌─────────────────────────────────────────────────────────┐
│  Open Panel Button (fixed bottom-right, always visible) │
└─────────────────────────────────────────────────────────┘

When panel opens (docked mode):
┌──────────────────────┬─────────────────────────────────────┐
│ Page Content (pushed │  Trade Assistant Panel (380px)      │
│ left by 404px)       │  ┌─────────────────────────────────┤
│                      │  │ Close [×]                        │
│                      │  ├─────────────────────────────────┤
│                      │  │ Context Header (sticky)          │
│                      │  │ - Current Event                  │
│                      │  │ - Outlet Stance (Support/etc)    │
│                      │  │ - Key Voices (Analysts)          │
│                      │  ├─────────────────────────────────┤
│                      │  │ Market Context                   │
│                      │  │ Directional Ideas (scrollable)   │
│                      │  │                                  │
│                      │  │                                  │
│                      │  │                                  │
│                      │  └─────────────────────────────────┘
└──────────────────────┴─────────────────────────────────────┘
```

## Key Design Decisions

1. **Context Header Always At Top**: Sticky positioning ensures it's visible while scrolling through market data
2. **No Storage Spam**: Debounced at 500ms; only persists critical state changes
3. **No Shadow Root Recreation**: Created once, only updated on render
4. **Page Push Mechanism**: Uses `paddingRight` on `documentElement` to prevent content overlap
5. **Floating Mode Disabled Interactions**: Drag and resize are mode-aware
6. **Mock Data by Default**: All data is hardcoded for now; can be replaced with API calls later

## Testing Checklist

- ✅ Panel opens/closes without recreating shadow roots
- ✅ Docked mode pushes page content to the left
- ✅ Page push removes when panel closes
- ✅ Floating mode allows drag and resize
- ✅ ContextHeader displays outlets, analysts, and current event
- ✅ Layout mode toggle works (via state.layoutMode)
- ✅ No TypeScript errors
- ✅ No unused variable warnings
- ✅ Storage persists layoutMode on page reload

## Future Enhancements

1. Add real news API integration to fetch outlet data
2. Replace mock analyst quotes with real data
3. Add filtering/sorting of outlets by stance or confidence
4. Layout mode toggle button in panel header
5. Responsive design for mobile
6. Customize outlet refresh frequency
7. Connection to real market APIs for slug extraction

## Edge Cases Handled

- Panel closes/opens multiple times without state corruption
- Page scrolling doesn't affect floating mode dragging
- Docked mode respects viewport height (bottom: 16px)
- layoutMode persistence across page reloads
- Graceful fallback to defaults if storage is empty
