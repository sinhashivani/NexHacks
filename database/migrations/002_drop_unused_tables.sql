-- Migration: Drop Unused Tables
-- Drops all tables except 'markets' and 'parlay_suggestions'
-- Run this in Supabase SQL Editor

-- Drop tables in order (CASCADE will handle foreign key dependencies)
-- Tables to drop:
--   - hedge_opportunities (references user_trades and markets)
--   - trade_correlations (references markets)
--   - related_trades (references markets)
--   - user_trades (references markets)

-- 1. Drop hedge_opportunities (references user_trades and markets)
DROP TABLE IF EXISTS hedge_opportunities CASCADE;

-- 2. Drop trade_correlations (references markets)
DROP TABLE IF EXISTS trade_correlations CASCADE;

-- 3. Drop related_trades (references markets)
DROP TABLE IF EXISTS related_trades CASCADE;

-- 4. Drop user_trades (references markets)
DROP TABLE IF EXISTS user_trades CASCADE;

-- Verify remaining tables (should only show markets and parlay_suggestions)
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
