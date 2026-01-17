# Changes from Original PRD

## Major Changes

### 1. Interaction Model Changed
- **Before**: Detected Buy/Sell/Confirm button clicks
- **After**: Detects hover on market cards/outcome rows (250ms debounce) and trade module opening

### 2. Storage Model Changed
- **Before**: `TradeIntent` with `status: 'attempted'`
- **After**: `MarketInteraction` with `interaction_type: 'hover_open' | 'ticket_open'`

### 3. Trigger Mechanism
- **Before**: Overlay opened after user clicked Buy/Sell/Confirm
- **After**: Overlay opens on:
  - Hover over market card/outcome row (250ms debounce)
  - Trade module/ticket becomes visible
  - Fallback button click

### 4. New Features Added
- **Pin Toggle**: User can pin current Primary Trade to prevent hover updates
- **Rate Limiting**: Max 1 backend call per second (unless user pins new primary)
- **Hover Detection**: Document-level pointer events with debouncing
- **Trade Module Detection**: MutationObserver watches for trade ticket visibility

### 5. Request/Response Changes
- **Request**: Added `trigger_type: 'hover' | 'ticket_open'` to PrimaryMarket
- **Request**: Changed `recent_trades` to `recent_interactions` in LocalProfile
- **Response**: Same structure (no changes needed)

## Files Changed

### Extension
- ✅ `src/types/index.ts` - Updated to MarketInteraction
- ✅ `src/utils/storage.ts` - Changed to market interactions
- ✅ `src/utils/interactionDetection.ts` - NEW: Hover + trade module detection
- ❌ `src/utils/tradeDetection.ts` - DELETED (replaced by interactionDetection)
- ✅ `src/components/Overlay.tsx` - Added Pin toggle, hover update logic
- ✅ `src/content/content.tsx` - Rewritten for hover/ticket detection
- ✅ `src/content/shadowStyles.ts` - Added pin button styles

### Backend
- ✅ `routers/recommendations.py` - Updated request types
- ✅ `services/recommendation_engine.py` - Changed recent_trades to recent_interactions
- ✅ `services/scoring.py` - Updated recency weighting parameter name

## Implementation Details

### Hover Detection
- Uses `pointerenter`/`pointerleave` at document level
- 250ms debounce before triggering
- Heuristics to identify market cards:
  - Links to `/event/`
  - Data attributes with "market" or "event"
  - Class names containing "market-card" or "event-card"

### Trade Module Detection
- MutationObserver watches for trade ticket visibility
- Checks multiple selectors for trade module
- Detects when module becomes visible (not just when it exists)

### Rate Limiting
- Tracks last call time
- Blocks calls if < 1 second since last call
- Exception: User can pin a new primary (allows immediate update)

### Pin Behavior
- When pinned: Hover does not update Primary Trade
- When unpinned: Hover updates Primary Trade automatically
- Pin state persists until user toggles it

## Testing Checklist

- [ ] Hover over market card opens overlay after 250ms
- [ ] Moving cursor across multiple cards doesn't spam backend
- [ ] Trade module opening triggers overlay
- [ ] Pin toggle prevents hover updates
- [ ] Unpinning allows hover updates again
- [ ] Rate limiting works (max 1 call/second)
- [ ] Fallback button works
- [ ] Recommendations load correctly
- [ ] Basket builder works
- [ ] SPA navigation handled correctly
