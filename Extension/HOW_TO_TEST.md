# How to Test - MVP Extension

## Build Steps

1. **Install Dependencies**:
   ```bash
   cd Extension
   npm install
   ```

2. **Build Extension**:
   ```bash
   npm run build
   ```

3. **Load in Chrome**:
   - Open `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `Extension/dist` folder

## Test Checklist

### 1. Panel Appears on Market Pages
- [ ] Navigate to `https://polymarket.com/event/...` (any market page)
- [ ] Panel should appear on the right side automatically
- [ ] Page content should be shifted left (not covered by panel)
- [ ] Panel shows current market title and URL

### 2. Resizable Panel
- [ ] Hover over left edge of panel - cursor should change to resize
- [ ] Drag left edge to resize panel
- [ ] Panel width should be between 280px and 560px
- [ ] Page margin should adjust as panel resizes
- [ ] Panel width should persist after page reload

### 3. Minimize/Close
- [ ] Click minimize button (-) - panel should collapse to slim bar
- [ ] Page margin should reduce to 60px when minimized
- [ ] Click restore button (→) - panel should expand
- [ ] Click close button (×) - panel should disappear
- [ ] Page margin should return to 0 when closed
- [ ] Fallback button should appear when closed
- [ ] Click fallback button - panel should reopen

### 4. Trade Card
- [ ] Shows current market title
- [ ] Shows current market URL
- [ ] If side (YES/NO) is detected, shows it
- [ ] If amount is detected, shows it
- [ ] Updates when navigating to different market

### 5. Recommendations (Placeholder)
- [ ] Amplify tab shows 5 sample markets
- [ ] Hedge tab shows 5 sample markets
- [ ] Each recommendation shows: title, category, score, reason
- [ ] "Open" button opens market in new tab
- [ ] "Add to Basket" button adds to basket
- [ ] Recommendations regenerate on each page load

### 6. Basket Builder
- [ ] Shows primary market + added legs
- [ ] Remove leg button (×) removes leg
- [ ] "Open Next Unvisited" opens first unvisited leg
- [ ] Visited state updates when leg is opened
- [ ] Basket persists across page reloads

### 7. Pinned Orders
- [ ] Click "Pin Current" - adds current market to pinned list
- [ ] Pinned item shows: title, URL, timestamp
- [ ] "Open" button opens pinned market in new tab
- [ ] "×" button removes pinned item
- [ ] Up/Down arrows reorder pinned items
- [ ] "Add Notes" / "Edit" allows editing notes
- [ ] Notes save and persist
- [ ] Pinned orders persist across browser restarts (chrome.storage.sync)

### 8. History
- [ ] Visiting markets adds them to history
- [ ] Shows last 50 items
- [ ] "Show All" expands to show all history
- [ ] "Open" opens history item in new tab
- [ ] "Pin" pins item from history
- [ ] History persists across browser restarts

### 9. SPA Navigation
- [ ] Navigate between markets (SPA routing)
- [ ] Panel should update with new market info
- [ ] Panel should not duplicate
- [ ] Page margin should remain correct
- [ ] History should track each market visit

### 10. Persistence
- [ ] Close browser and reopen
- [ ] Panel state (open/minimized/width) should persist
- [ ] Pinned orders should persist
- [ ] History should persist
- [ ] Basket should persist

### 11. Non-Market Pages
- [ ] Navigate to non-market page (e.g., homepage)
- [ ] Panel should close automatically
- [ ] Page margin should return to 0
- [ ] Navigate back to market page
- [ ] Panel should reopen if it was open before

## Expected Behavior

- **Panel is always-on** on market pages (unless manually closed)
- **Panel adjusts page layout** (doesn't overlay content)
- **All data persists** using chrome.storage.sync
- **No backend required** - everything is client-side
- **Recommendations are placeholder** - randomly generated from sample list

## Troubleshooting

- **Panel doesn't appear**: Check browser console for errors
- **Panel covers content**: Verify page margin is being set correctly
- **Data doesn't persist**: Check chrome.storage.sync in DevTools → Application → Storage
- **Resize doesn't work**: Check that resize handle is visible and clickable
