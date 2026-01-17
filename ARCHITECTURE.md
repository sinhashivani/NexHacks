# Architecture & Data Flow Diagram

## Component Hierarchy

```
content.tsx (Content Script)
│
├── Shadow Host (single instance)
│   └── Shadow Root
│       ├── <style> (shadowStyles)
│       └── Panel Element (fixed positioning)
│           └── React Root
│               └── FloatingAssistant
│                   ├── Header
│                   │   └── Close Button
│                   ├── ContextHeader (sticky)
│                   │   ├── Current Event
│                   │   ├── Outlet Stance (4 outlets)
│                   │   └── Key Voices (2 analysts)
│                   ├── Market Context
│                   └── DirectionalIdeas
│                       └── Trade Recommendations
│
├── Open Panel Button (document.body)
│
└── Event Listeners
    ├── Store subscription → render()
    ├── History watcher
    └── Route change detector

Alongside (outside Shadow DOM):
└── overlayStore (Singleton)
    └── chrome.storage.sync
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interaction                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Button Click   │
                    │  Header Drag    │
                    │  Resize Corner  │
                    └────────┬────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │  FloatingAssistant Event Handlers      │
        │  (handleHeaderPointerDown, etc)        │
        └────────┬─────────────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────┐
    │ onStateChange() callback     │
    │ (passed from content.tsx)    │
    └────────┬─────────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │  overlayStore.setState()   │
    │  (Updates in-memory state) │
    └────────┬───────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
  ┌─────────┐  ┌──────────────────────┐
  │Immediate│  │ Debounce Timer (500ms)
  │Notify   │  │ (Only if changed)
  │Listeners│  │ └──→ chrome.storage.sync.set()
  └────┬────┘  └──────────────────────┘
       │
       ▼
┌────────────────────────┐
│ content.tsx listener   │
│ (store.subscribe)      │
└────────┬───────────────┘
         │
         ▼
    ┌─────────────┐
    │ render(state)
    │ function    │
    └────────┬────┘
             │
      ┌──────┴─────────────┐
      │                    │
      ▼                    ▼
  ┌─────────────┐  ┌──────────────────┐
  │Apply/Remove │  │ Update Panel     │
  │Page Push    │  │ Position & Size  │
  │(paddingRight)│  │(left/top/right/  │
  │             │  │ width/height)    │
  └─────────────┘  └────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ React.render()    │
                  │ (Re-render UI)    │
                  └────────┬──────────┘
                           │
                           ▼
                  ┌───────────────────┐
                  │  Updated Panel    │
                  │  Displays on Page │
                  └───────────────────┘
```

## State Shape

```typescript
OverlayState {
  open: boolean           // Visibility toggle
  width: number          // Panel width (default 380)
  height: number         // Panel height (default 720)
  x: number              // Floating mode left position
  y: number              // Floating mode top position
  layoutMode: 'docked'   // Layout mode ('docked' | 'floating')
           | 'floating'
}

PageContext {
  title: string         // document.title
  url: string           // location.href
  slug: string          // Extracted from URL/title
}

Outlet {
  name: string          // 'WSJ', 'Bloomberg', etc
  stance: OutletStance  // 'Support' | 'Neutral' | 'Oppose'
  confidence: number    // 65-85 (percentage)
  rationale: string     // 1-sentence explanation
}

Analyst {
  name: string          // 'A. Chen', 'M. Rivera', etc
  role: string          // 'Macro Analyst', 'Rates Trader'
  quote: string         // Direct quote about market thesis
}
```

## Positioning Logic

### Docked Mode
```
┌─────────────────────────────────────────────────────────┐
│ Browser Viewport (window.innerWidth)                    │
│                                                         │
│ Page Content (pushed left)                 Panel (380px) │
│                                            │            │
│ margin/padding-right: 404px               ┌────────────┐│
│                                           │ Close [×] ││
│                                           ├────────────┤│
│                                           │ Context    ││
│                                           │ Header     ││
│                                           │ (sticky)   ││
│                                           │            ││
│                                           │ Market     ││
│                                           │ Context    ││
│                                           │            ││
│                                           │ Ideas      ││
│                                           │ (scroll)   ││
│                                           └────────────┘│
└─────────────────────────────────────────────────────────┘

CSS Applied:
- Panel: position: fixed; right: 16px; top: 16px; bottom: 16px; width: 380px
- Page: document.documentElement.style.paddingRight = "404px" (380 + 24)
```

### Floating Mode
```
┌─────────────────────────────────────────────────────────┐
│ Browser Viewport                                        │
│                                                         │
│     ┌──────────────────┐                                │
│     │ Close [×]        │ (draggable header)             │
│     ├──────────────────┤                                │
│     │ Context Header   │                                │
│     │ (sticky)         │                                │
│     ├──────────────────┤                                │
│     │ Market Context   │                                │
│     │                  │                                │
│     │ Ideas            │                                │
│     │ (scrollable)     │                                │
│     ├──────────────────┐                                │
│     │              ◳◳ │ (resize handle, bottom-right)   │
│     └──────────────────┘                                │
│                                                         │
│ Page Content (No push, full width)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘

CSS Applied:
- Panel: position: fixed; left: x; top: y; width: width; height: height
- No page push (paddingRight = "")
```

## Event Flow: Panel Drag (Floating Mode)

```
1. User presses header area
   └─→ handleHeaderPointerDown()
       ├─ Check: Not clicking action buttons
       ├─ Check: layoutMode === 'floating'
       ├─ setIsDragging(true)
       ├─ Capture pointer: headerRef.current.setPointerCapture()
       └─ Record dragStart { clientX, clientY }

2. User moves mouse (while button held)
   └─→ handlePointerMove() listener
       ├─ Calculate delta: {deltaX, deltaY}
       ├─ New position: {newX, newY} = {x + deltaX, y + deltaY}
       ├─ Constrain to viewport bounds
       └─ onStateChange({x: constrainedX, y: constrainedY})

3. State changes
   └─→ overlayStore.setState()
       ├─ Update in-memory state immediately
       ├─ Notify listeners (content.tsx render)
       └─ Start debounce timer (500ms)

4. content.tsx render() called
   └─→ updatePanelPosition(state)
       └─ Set panelEl.style.left and .top

5. React re-renders
   └─→ FloatingAssistant component updates
       └─ UI reflects new position

6. User releases mouse
   └─→ handlePointerUp()
       ├─ setIsDragging(false)
       └─ Release pointer capture

7. After 500ms (debounce)
   └─→ chrome.storage.sync.set() saves state
```

## Event Flow: Page Push (Docked Mode)

```
1. User clicks Open Button
   └─→ overlayStore.setOpen(true)
       └─ setState({open: true})

2. State update notifies listeners
   └─→ render(state) in content.tsx

3. render() calls:
   └─→ updatePanelPosition(state)
       ├─ Check: layoutMode === 'docked'
       └─ Set: right, top, bottom, width styles

4. render() calls:
   └─→ applyPagePush(state)
       ├─ Check: layoutMode === 'docked' && open
       └─ Set: document.documentElement.style.paddingRight = "404px"

5. Browser reflows
   └─→ Page content shifts left by 404px
       └─ Panel appears on right side

6. User clicks Close Button
   └─→ overlayStore.setOpen(false)

7. render() calls applyPagePush(state)
   └─→ paddingRight = "" (removes padding)
       └─ Page content returns to full width

8. render() hides panel
   └─→ panelEl.style.display = "none"
```

## Storage Persistence Timeline

```
Time    Action                  Storage
────────────────────────────────────────────────
0ms     User drags panel        (in-memory state updates)
50ms    Still dragging          (in-memory state updates)
100ms   Still dragging          (in-memory state updates)
        └─ Clear debounce timer, restart
150ms   Still dragging          (in-memory state updates)
200ms   User releases mouse     (last state update)
        └─ Start 500ms debounce timer
500ms   │
        └─→ Debounce fires
             │
             ├─ Check: Did {open, x, y, width, height, layoutMode} change?
             ├─ Yes → chrome.storage.sync.set(state)
             └─ No → Skip write (avoid quota hits)
```

## Component Reusability

```
ContextHeader
├─ Standalone component
├─ Gets data from contextData.ts
├─ No props required
├─ Can be embedded in other panels
└─ All styling inline (shadow DOM safe)

pageContext (Unused in current version)
├─ Standalone component
├─ Displays event info
├─ Could be moved to panel body
└─ For future UI enhancements

contextData.ts Module
├─ Pure utilities (no React)
├─ Can be imported anywhere
├─ Easily swappable for API calls
└─ Mock data generators for testing
```

## Error Handling Paths

```
1. Storage not available
   └─ getOverlayState() catch block
       └─ Return defaults with layoutMode: 'docked'

2. Panel element not found
   └─ render() checks panelEl && reactRoot
       └─ Log error, skip render

3. Drag outside viewport
   └─ updatePanelPosition() constraints applied
       └─ Math.max/min keep within bounds

4. Rapid open/close clicks
   └─ ensureUiOnce() returns early if already initialized
       └─ Single React root reused

5. Missing layoutMode in saved state
   └─ storage.ts default includes layoutMode
       └─ Graceful fallback to 'docked'
```
