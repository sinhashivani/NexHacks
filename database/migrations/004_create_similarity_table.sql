-- Migration: Create Similarity Scores Table and Add event_title to Markets
-- Stores similarity scores between markets based on cosine similarity
-- Run this in Supabase SQL Editor

-- Add event_title column to markets table if it doesn't exist
ALTER TABLE markets ADD COLUMN IF NOT EXISTS event_title TEXT;

-- Create index on event_title for faster lookups
CREATE INDEX IF NOT EXISTS idx_markets_event_title ON markets(event_title);

-- Create similarity_scores table
CREATE TABLE IF NOT EXISTS similarity_scores (
    id BIGSERIAL PRIMARY KEY,
    source_clob_token_ids TEXT NOT NULL,
    neighbor_clob_token_ids TEXT NOT NULL,
    cosine_similarity NUMERIC(10, 8) NOT NULL CHECK (cosine_similarity >= 0 AND cosine_similarity <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for similarity_scores
CREATE INDEX IF NOT EXISTS idx_similarity_source ON similarity_scores(source_clob_token_ids);
CREATE INDEX IF NOT EXISTS idx_similarity_neighbor ON similarity_scores(neighbor_clob_token_ids);
CREATE INDEX IF NOT EXISTS idx_similarity_score ON similarity_scores(cosine_similarity DESC);

-- Composite index for faster lookups
CREATE INDEX IF NOT EXISTS idx_similarity_source_score ON similarity_scores(source_clob_token_ids, cosine_similarity DESC);
