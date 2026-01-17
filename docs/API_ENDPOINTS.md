# API Endpoints Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "name": "NexHacks Polymarket API",
  "version": "1.0.0",
  "endpoints": {
    "trending": "/markets/trending",
    "ui": "/ui"
  }
}
```

---

### GET `/markets/trending`
Get trending/popular markets ranked by popularity.

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "politics", "sports", "tech", "economy")
- `limit` (optional, default: 20): Maximum number of results (1-100)
- `min_score` (optional, default: 0.0): Minimum trending score threshold (0.0-1.0)

**Example Request:**
```
GET /markets/trending?category=politics&limit=10
```

**Response:**
```json
{
  "count": 10,
  "markets": [
    {
      "market_id": "824952",
      "market_slug": "microstrategy-sells-any-bitcoin-by-december-31-2026",
      "question": "MicroStrategy sells any Bitcoin by December 31, 2026?",
      "canonical_category": "economy",
      "trending_score": 0.8723,
      "open_interest": 12345.67,
      "volume_24h": 2345.0,
      "liquidity": 567.89,
      "last_price": 0.63
    }
  ]
}
```

**Trending Score Calculation:**
The trending score is calculated using a weighted formula:
- 50% weight on open interest
- 30% weight on 24-hour volume
- 20% weight on liquidity

Scores are normalized and range from 0.0 to 1.0, with higher scores indicating more popular/trending markets.

---

### GET `/markets/trending/refresh`
Refresh market metrics from Polymarket API.

This endpoint fetches the latest market data from Polymarket and updates the `market_metrics` table. Call this periodically to keep trending data fresh.

**Query Parameters:**
- `limit` (optional, default: 100): Number of markets to fetch from Polymarket (1-500)

**Example Request:**
```
GET /markets/trending/refresh?limit=200
```

**Response:**
```json
{
  "success": true,
  "markets_updated": 150,
  "message": "Updated metrics for 150 markets"
}
```

**Note:** This endpoint may take some time to complete as it fetches data from Polymarket API for each market.

---

### GET `/ui`
Get market UI data by CLOB token ID (existing endpoint).

**Query Parameters:**
- `token_id` (required): CLOB token ID

**Example Request:**
```
GET /ui?token_id=111128191581505463501777127559667396812474366956707382672202929745167742497287
```

**Response:**
```json
{
  "q": "MicroStrategy sells any Bitcoin by December 31, 2026?",
  "img": "https://...",
  "p": {
    "Yes": "0.63",
    "No": "0.37"
  }
}
```

---

## Setup Instructions

### 1. Create Market Metrics Table

Run the migration SQL in Supabase SQL Editor:

```sql
-- See database/migrations/003_create_market_metrics.sql
```

### 2. Initial Data Refresh

Before using the trending endpoint, refresh market metrics:

```bash
curl http://localhost:8000/markets/trending/refresh?limit=100
```

### 3. Periodic Updates

Set up a cron job or scheduled task to refresh metrics periodically (e.g., every 15-30 minutes):

```bash
# Example cron job (every 30 minutes)
*/30 * * * * curl http://localhost:8000/markets/trending/refresh?limit=200
```

---

## Testing

### Start the API server:
```bash
uvicorn api:app --reload
```

### Test trending endpoint:
```bash
curl http://localhost:8000/markets/trending?limit=5
```

### Test with category filter:
```bash
curl http://localhost:8000/markets/trending?category=politics&limit=10
```

---

## Notes

- Trending scores are calculated based on market metrics (open interest, volume, liquidity)
- If a market has no metrics yet, it will have a score of 0.0 and won't appear in results unless `min_score=0.0`
- The refresh endpoint should be called regularly to keep data current
- Category filtering uses the `tag_label` field from the markets table
