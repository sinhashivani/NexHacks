# Polymarket Trade Assistant

A Chrome Extension (Manifest V3) that provides trade recommendations on Polymarket.com market pages. The extension overlays recommendations for amplifying or hedging trades, with a portfolio-aware recommendation engine.

## Architecture

### Extension
- **Tech Stack**: Vite + React + TypeScript
- **Manifest**: V3
- **Injection**: Shadow DOM overlay (isolated from site CSS)
- **Trade Detection**: MutationObserver + click listeners for Buy/Sell/Confirm buttons
- **Storage**: chrome.storage.local for trade intents

### Backend
- **Tech Stack**: FastAPI + MongoDB + Motor (async)
- **APIs**: Gamma API, CLOB API, Gemini API
- **Features**: Market discovery, similarity scoring, correlation computation, caching

## Project Structure

```
NexHacks/
├── Extension/              # Chrome Extension
│   ├── src/
│   │   ├── content/        # Content script with Shadow DOM injection
│   │   ├── background/     # Service worker
│   │   ├── components/     # React components (Overlay, Tabs, etc.)
│   │   ├── utils/          # Storage, API, trade detection
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── backend/                # FastAPI backend
│   ├── clients/            # API clients (Gamma, CLOB, Gemini)
│   ├── services/           # Business logic (scoring, correlation, cache)
│   ├── routers/            # API endpoints
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set:
   # - MONGODB_URI (default: mongodb://localhost:27017)
   # - MONGODB_DB_NAME (default: polymarket_assistant)
   # - GEMINI_API_KEY (required for entity extraction)
   ```

3. **Start MongoDB** (if not running):
   ```bash
   # Using Docker:
   docker run -d -p 27017:27017 mongo:latest
   
   # Or use your existing MongoDB instance
   ```

4. **Run the backend**:
   ```bash
   python run.py
   # Or:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at `http://localhost:8000`

### Extension Setup

1. **Install dependencies**:
   ```bash
   cd Extension
   npm install
   ```

2. **Configure backend URL** (optional):
   Create `.env` file in `Extension/`:
   ```
   VITE_BACKEND_URL=http://localhost:8000
   ```

3. **Build the extension**:
   ```bash
   npm run build
   ```

4. **Load in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `Extension/dist` directory

## Features

### Extension Features
- **Overlay UI**: Top-right drawer panel with Close and Minimize
- **Trade Detection**: Automatically opens overlay when user clicks Buy/Sell/Confirm
- **Fallback Button**: Floating button to manually open overlay
- **Primary Trade Card**: Shows market title, URL, side (YES/NO), amount, topic
- **Two Tabs**: Amplify and Hedge recommendations (5 markets each)
- **Basket Builder**: Track primary + added legs, visited state, open next unvisited
- **Performance**: <1.5s cached, <3s uncached with skeleton loading

### Backend Features
- **Market Resolution**: Resolve market metadata from Gamma API
- **Topic Discovery**: Discover markets in locked topics (Finance, Politics, Technology, Elections, Economy)
- **Similarity Scoring**: Semantic similarity + entity overlap
- **Hedging Logic**: Correlation-based hedging recommendations
- **5-Market Set**: Primary + 2 from history + 2 top amplify
- **Correlation Matrix**: Pearson correlation on returns (7d/30d windows)
- **Caching**: Market metadata and price history caching

## API Endpoints

### POST /v1/recommendations
Generate amplify and hedge recommendations.

**Request**:
```json
{
  "primary": {
    "url": "https://polymarket.com/event/...",
    "side": "YES",
    "amount": 100
  },
  "local_profile": {
    "recent_trades": [...],
    "topic_counts": {...},
    "entity_counts": {...}
  }
}
```

**Response**:
```json
{
  "primary_resolved": {
    "market_id": "...",
    "title": "...",
    "slug": "...",
    "token_ids": [...],
    "topics": [...]
  },
  "amplify": [...],
  "hedge": [...],
  "five_set": [...],
  "corr": {
    "window_used": "30d",
    "matrix": [[...], [...]],
    "coverage": 0.8
  }
}
```

### GET /v1/tags
Get resolved tag IDs for locked topics.

**Response**:
```json
{
  "tags": {
    "Finance": {"id": 1, "label": "Finance"},
    "Politics": {"id": 2, "label": "Politics"},
    ...
  }
}
```

## Test Plan

### Trade Detection Testing
1. Navigate to a Polymarket market page
2. Click Buy or Sell button
3. Verify overlay opens automatically
4. Verify primary trade card shows detected side/amount
5. Test fallback button if detection fails

### Recommendation Latency Testing
1. Open overlay on a market page
2. Measure time to show recommendations:
   - First load (uncached): Should be <3s
   - Subsequent loads (cached): Should be <1.5s
3. Verify skeleton loading appears during fetch
4. Verify recommendations appear with scores and reasons

### Basket Builder Testing
1. Add legs from Amplify/Hedge tabs
2. Verify legs appear in basket
3. Click "Open Next Unvisited" - should open in new tab
4. Verify visited state updates
5. Remove legs and verify removal

### Backend Testing
1. Test `/v1/tags` endpoint - should return 5 topic tags
2. Test `/v1/recommendations` with valid market URL
3. Verify response includes 5 amplify + 5 hedge recommendations
4. Verify 5-market set includes primary + 4 others
5. Verify correlation matrix when price data available

## Development Notes

### Trade Detection
- Uses MutationObserver for SPA navigation
- Listens for Buy/Sell/Confirm button clicks
- Extracts side (YES/NO) and amount from button context
- Falls back to manual button if detection fails

### Shadow DOM
- Overlay is injected into Shadow DOM to isolate from site CSS
- Styles are scoped to shadow root
- React mounts inside shadow container

### Caching
- Market metadata cached for 24 hours
- Price history cached for 1 hour
- Recommendations cached for 1 minute (in extension)

### 5-Market Set Rule
1. Market 1: Primary market
2. Markets 2-3: Most relevant from local history (recency-weighted)
3. Markets 4-5: Top amplify candidates by score

### Correlation Computation
- Uses Pearson correlation on returns
- Tries 30d window first, falls back to 7d
- Returns null if insufficient data (<5 data points)

## Security

- Gemini API key stored only in backend (never in extension)
- CORS restricted to extension origin
- No automated trading - all recommendations are UI guidance only
- No wallet address collection

## Troubleshooting

### Extension not loading
- Check `dist/manifest.json` exists
- Verify all files built correctly
- Check Chrome extension console for errors

### Backend connection errors
- Verify backend is running on port 8000
- Check `VITE_BACKEND_URL` in extension `.env`
- Verify CORS settings allow extension origin

### No recommendations
- Check backend logs for API errors
- Verify Gemini API key is set
- Check MongoDB connection
- Verify Gamma/CLOB API endpoints are accessible

## License

MIT
