# Quick Testing Guide

## Setup
1. Build the extension: `npm run build` or `yarn build`
2. Load in Chrome: `chrome://extensions` → Load unpacked → select `Extension` folder

## Test Cases

### 1. Basic Panel Open/Close (Repeat 5x)
- [ ] Click "Open panel" button → Panel appears on right side
- [ ] Check: Page content is pushed left
- [ ] Click "×" close button → Panel disappears
- [ ] Check: Page content returns to normal width
- [ ] Verify no console errors

### 2. Docked Mode Page Push
- [ ] Open panel → Check `document.documentElement.style.paddingRight`
- [ ] Should be set to `404px` (380 + 24)
- [ ] Scroll page → Panel stays fixed on right
- [ ] Close panel → paddingRight removed
- [ ] Open panel again → paddingRight re-applied

### 3. Context Header Content
- [ ] Open panel
- [ ] Check header shows:
  - [x] Current Event title
  - [x] URL
  - [x] Inferred slug
  - [x] Top 4 outlets with stance badges
  - [x] Outlet confidence percentages
  - [x] Outlet rationale text
  - [x] Top 2 analysts with role and quote

### 4. Shadow DOM Check
- [ ] Open DevTools → Elements
- [ ] Find `<div id="pm-overlay-host">`
- [ ] Expand shadow root
- [ ] Verify only ONE shadow host exists
- [ ] Open/close panel 10 times
- [ ] Still only ONE shadow host (not recreated)

### 5. State Persistence
- [ ] Open panel
- [ ] Refresh page
- [ ] Panel should appear in same state
- [ ] Change layout mode (if button exists)
- [ ] Refresh page
- [ ] Layout mode persisted

### 6. Console Logs
- [ ] Open DevTools → Console
- [ ] Look for `[CONTENT]`, `[STORE]`, `[STORAGE]` prefixed logs
- [ ] Should NOT see "Removing orphaned container" or "Creating new shadow root" on every interaction
- [ ] Should see proper debounce behavior on state changes

### 7. Button Interactivity
- [ ] "Open panel" button is fully clickable
- [ ] Hover effects work
- [ ] Click from anywhere on button text (not just one spot)

### 8. Outlet Stance Colors
- [ ] Support outlets have green left border
- [ ] Neutral outlets have orange left border
- [ ] Oppose outlets have red left border

### 9. Scrolling in Header
- [ ] Large amounts of outlet/analyst data should scroll within panel
- [ ] Header (ContextHeader) stays sticky at top
- [ ] Content below scrolls independently

### 10. Floating Mode (If Toggle Exists)
- [ ] Switch to floating mode
- [ ] Drag header to move panel
- [ ] Resize from bottom-right corner
- [ ] Switch back to docked mode
- [ ] Panel repositions to dock position

## Known Limitations (As Designed)

- All outlet/analyst data is hardcoded
- No real news API integration yet
- Layout mode toggle requires code change (not UI button yet)
- Outlet data doesn't change based on event/market slug (could be future feature)

## Debugging Tips

### Shadow DOM Not Visible?
```javascript
// In console:
document.querySelector('#pm-overlay-host').shadowRoot
```

### Check Current State?
```javascript
// In background script console:
chrome.storage.sync.get('overlay_state', console.log)
```

### Verify Panel Position?
```javascript
// In page console:
const panel = document.querySelector('#pm-overlay-host')?.shadowRoot?.querySelector('#pm-overlay-panel');
console.log('Position:', {
  left: panel?.style.left,
  top: panel?.style.top,
  right: panel?.style.right,
  width: panel?.style.width
});
```

### Check Storage Writes
- Open DevTools → Application → Chrome Storage → sync
- Look for `overlay_state` key
- Should only update when you stop dragging/resizing (debounce)
- Not on every mousemove

## Common Issues

**Issue**: Panel doesn't appear docked on right
- **Fix**: Check browser zoom is 100%
- **Fix**: Check panel width isn't 0 or negative

**Issue**: Page content not pushed left
- **Fix**: Check `document.documentElement.style.paddingRight` value
- **Fix**: Browser zoom reset to 100%

**Issue**: Multiple shadow roots
- **Fix**: Hard refresh page (Ctrl+Shift+R)
- **Fix**: Clear extension data and reload

**Issue**: Outlet data not showing
- **Fix**: Check `contextData.ts` is properly imported
- **Fix**: Check network tab for API errors (shouldn't have any - all mock data)

## Performance Checks

1. **No Layout Thrashing**: Page scrolling should be smooth
2. **No Memory Leaks**: Open/close panel 20 times → memory should stabilize
3. **Storage Quota**: Debounce prevents hitting MAX_WRITE_OPERATIONS_PER_HOUR quota
