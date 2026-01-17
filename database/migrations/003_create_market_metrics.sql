-- Migration: Create Market Metrics Table
-- Stores live market metrics for trending calculations
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS market_metrics (
    market_id TEXT PRIMARY KEY REFERENCES markets(market_id) ON DELETE CASCADE,
    last_price NUMERIC,
    open_interest NUMERIC,
    volume_24h NUMERIC,
    liquidity NUMERIC,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for market_metrics
CREATE INDEX IF NOT EXISTS idx_market_metrics_updated_at ON market_metrics(updated_at);
CREATE INDEX IF NOT EXISTS idx_market_metrics_open_interest ON market_metrics(open_interest DESC);
CREATE INDEX IF NOT EXISTS idx_market_metrics_volume_24h ON market_metrics(volume_24h DESC);

-- Function to update updated_at timestamp
CREATE TRIGGER update_market_metrics_updated_at BEFORE UPDATE ON market_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
