-- Migration: Create Related Trades Table
-- Creates the related_trades table for storing market relationships

-- 4. Related Trades Table - Pairs trading opportunities
CREATE TABLE IF NOT EXISTS related_trades (
    id BIGSERIAL PRIMARY KEY,
    market_id TEXT NOT NULL REFERENCES markets(market_id),
    related_market_id TEXT NOT NULL REFERENCES markets(market_id),
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('company_pair', 'sector', 'event', 'geographic')),
    relationship_strength DECIMAL(5, 4) NOT NULL CHECK (relationship_strength >= 0 AND relationship_strength <= 1),
    description TEXT,
    examples TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(market_id, related_market_id, relationship_type)
);

-- Indexes for related_trades
CREATE INDEX IF NOT EXISTS idx_related_market_id ON related_trades(market_id);
CREATE INDEX IF NOT EXISTS idx_related_related_market_id ON related_trades(related_market_id);
CREATE INDEX IF NOT EXISTS idx_related_type ON related_trades(relationship_type);
CREATE INDEX IF NOT EXISTS idx_related_strength ON related_trades(relationship_strength DESC);

-- Add comment
COMMENT ON TABLE related_trades IS 'Stores relationships between markets for trading pattern analysis';
COMMENT ON COLUMN related_trades.relationship_type IS 'Type of relationship: event, sector, company_pair, or geographic';
COMMENT ON COLUMN related_trades.relationship_strength IS 'Strength of relationship from 0.0 to 1.0';
