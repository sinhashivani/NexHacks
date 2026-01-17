-- Supabase Database Schema for NexHacks Polymarket Correlation Tool
-- Run this SQL in your Supabase SQL Editor

-- 1. Markets Table - Store Polymarket market data
CREATE TABLE IF NOT EXISTS markets (
    id BIGSERIAL PRIMARY KEY,
    market_id TEXT UNIQUE NOT NULL,
    market_slug TEXT,
    question TEXT NOT NULL,
    tag_label TEXT,
    tag_id INTEGER,
    clob_token_ids TEXT,
    active BOOLEAN DEFAULT TRUE,
    closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for markets
CREATE INDEX IF NOT EXISTS idx_markets_market_id ON markets(market_id);
CREATE INDEX IF NOT EXISTS idx_markets_tag_label ON markets(tag_label);
CREATE INDEX IF NOT EXISTS idx_markets_active ON markets(active);
CREATE INDEX IF NOT EXISTS idx_markets_question_search ON markets USING gin(to_tsvector('english', question));

-- 2. User Trades Table - Store user's trading history
CREATE TABLE IF NOT EXISTS user_trades (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    market_id TEXT NOT NULL REFERENCES markets(market_id),
    trade_type TEXT NOT NULL CHECK (trade_type IN ('yes', 'no')),
    shares INTEGER NOT NULL,
    price DECIMAL(10, 4) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'closed', 'cancelled')),
    notes TEXT
);

-- Indexes for user_trades
CREATE INDEX IF NOT EXISTS idx_user_trades_user_id ON user_trades(user_id);
CREATE INDEX IF NOT EXISTS idx_user_trades_market_id ON user_trades(market_id);
CREATE INDEX IF NOT EXISTS idx_user_trades_user_market ON user_trades(user_id, market_id);
CREATE INDEX IF NOT EXISTS idx_user_trades_timestamp ON user_trades(timestamp);

-- 3. Trade Correlations Table - Store calculated correlations
CREATE TABLE IF NOT EXISTS trade_correlations (
    id BIGSERIAL PRIMARY KEY,
    market_id_1 TEXT NOT NULL REFERENCES markets(market_id),
    market_id_2 TEXT NOT NULL REFERENCES markets(market_id),
    correlation_score DECIMAL(5, 4) NOT NULL CHECK (correlation_score >= -1 AND correlation_score <= 1),
    correlation_type TEXT NOT NULL CHECK (correlation_type IN ('related', 'correlated', 'inverse')),
    calculation_method TEXT,
    similarity_score DECIMAL(5, 4),
    price_correlation DECIMAL(5, 4),
    category_match BOOLEAN DEFAULT FALSE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confidence DECIMAL(5, 4),
    UNIQUE(market_id_1, market_id_2)
);

-- Indexes for trade_correlations
CREATE INDEX IF NOT EXISTS idx_correlations_market_1 ON trade_correlations(market_id_1);
CREATE INDEX IF NOT EXISTS idx_correlations_market_2 ON trade_correlations(market_id_2);
CREATE INDEX IF NOT EXISTS idx_correlations_score ON trade_correlations(correlation_score);
CREATE INDEX IF NOT EXISTS idx_correlations_type ON trade_correlations(correlation_type);

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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for related_trades
CREATE INDEX IF NOT EXISTS idx_related_market_id ON related_trades(market_id);
CREATE INDEX IF NOT EXISTS idx_related_related_market_id ON related_trades(related_market_id);
CREATE INDEX IF NOT EXISTS idx_related_type ON related_trades(relationship_type);

-- 5. Parlay Suggestions Table - Suggested parlay combinations
CREATE TABLE IF NOT EXISTS parlay_suggestions (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    base_market_id TEXT NOT NULL REFERENCES markets(market_id),
    suggested_markets JSONB NOT NULL,
    expected_return DECIMAL(10, 4) NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    confidence DECIMAL(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    viewed BOOLEAN DEFAULT FALSE,
    accepted BOOLEAN DEFAULT FALSE
);

-- Indexes for parlay_suggestions
CREATE INDEX IF NOT EXISTS idx_parlay_user_id ON parlay_suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_parlay_base_market ON parlay_suggestions(base_market_id);
CREATE INDEX IF NOT EXISTS idx_parlay_expected_return ON parlay_suggestions(expected_return);

-- 6. Hedge Opportunities Table - Hedge suggestions
CREATE TABLE IF NOT EXISTS hedge_opportunities (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    original_trade_id BIGINT REFERENCES user_trades(id),
    original_market_id TEXT NOT NULL REFERENCES markets(market_id),
    hedge_market_id TEXT NOT NULL REFERENCES markets(market_id),
    hedge_type TEXT NOT NULL CHECK (hedge_type IN ('inverse', 'opposite_outcome', 'uncorrelated')),
    inverse_correlation DECIMAL(5, 4) NOT NULL CHECK (inverse_correlation >= -1 AND inverse_correlation <= 1),
    hedge_ratio DECIMAL(5, 4) NOT NULL CHECK (hedge_ratio >= 0 AND hedge_ratio <= 1),
    risk_reduction DECIMAL(5, 4) NOT NULL CHECK (risk_reduction >= 0 AND risk_reduction <= 1),
    cost_impact DECIMAL(10, 2),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    viewed BOOLEAN DEFAULT FALSE,
    accepted BOOLEAN DEFAULT FALSE
);

-- Indexes for hedge_opportunities
CREATE INDEX IF NOT EXISTS idx_hedge_user_trade ON hedge_opportunities(user_id, original_trade_id);
CREATE INDEX IF NOT EXISTS idx_hedge_original_trade ON hedge_opportunities(original_trade_id);
CREATE INDEX IF NOT EXISTS idx_hedge_original_market ON hedge_opportunities(original_market_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_markets_updated_at BEFORE UPDATE ON markets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_related_trades_updated_at BEFORE UPDATE ON related_trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
