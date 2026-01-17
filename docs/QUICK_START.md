# Quick Start Guide - Trending Markets

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn supabase python-dotenv requests
```

### 2. Create Market Metrics Table

Go to Supabase Dashboard → SQL Editor and run:

```sql
-- Copy contents from database/migrations/003_create_market_metrics.sql
CREATE TABLE IF NOT EXISTS market_metrics (
    market_id TEXT PRIMARY KEY REFERENCES markets(market_id) ON DELETE CASCADE,
    last_price NUMERIC,
    open_interest NUMERIC,
    volume_24h NUMERIC,
    liquidity NUMERIC,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_metrics_updated_at ON market_metrics(updated_at);
CREATE INDEX IF NOT EXISTS idx_market_metrics_open_interest ON market_metrics(open_interest DESC);
CREATE INDEX IF NOT EXISTS idx_market_metrics_volume_24h ON market_metrics(volume_24h DESC);
```

### 3. Start the API Server

```bash
uvicorn api:app --reload
```

The API will be available at: `http://localhost:8000`

### 4. Initial Data Refresh

Before using trending markets, you need to fetch metrics from Polymarket:

```bash
# Using curl
curl http://localhost:8000/markets/trending/refresh?limit=100

# Or visit in browser
http://localhost:8000/markets/trending/refresh?limit=100
```

This will fetch market data from Polymarket and populate the `market_metrics` table.

### 5. Test Trending Endpoint

```bash
# Get top 10 trending markets
curl http://localhost:8000/markets/trending?limit=10

# Get trending politics markets
curl http://localhost:8000/markets/trending?category=politics&limit=10

# Or visit in browser
http://localhost:8000/markets/trending?limit=10
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Periodic Updates

To keep trending data fresh, refresh metrics periodically:

```bash
# Refresh every 30 minutes (example cron job)
*/30 * * * * curl http://localhost:8000/markets/trending/refresh?limit=200
```

Or set up a background job/scheduler to call the refresh endpoint automatically.

## Troubleshooting

### No markets returned?
- Make sure you've run the refresh endpoint first
- Check that markets exist in your database
- Verify market_metrics table was created

### Low trending scores?
- Markets need metrics (open_interest, volume, liquidity) to have scores > 0
- Run the refresh endpoint to populate metrics
- Some markets may have 0 metrics if Polymarket doesn't provide that data

### Category filter not working?
- Categories are based on `tag_label` field in markets table
- Available categories: politics, economy, tech, finance, elections, etc.
- Use lowercase category names
