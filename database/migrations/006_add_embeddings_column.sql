-- Migration: Add Embedding Column for Semantic Search
-- Adds embedding column to markets table for storing vector embeddings
-- Requires pgvector extension (Supabase has this enabled by default)

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to markets table
-- Using vector(768) for Gemini text-embedding-004 (768 dimensions)
ALTER TABLE markets ADD COLUMN IF NOT EXISTS embedding vector(768);

-- Create index for vector similarity search (using cosine distance)
CREATE INDEX IF NOT EXISTS idx_markets_embedding_cosine 
ON markets 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Note: To populate embeddings, you'll need to:
-- 1. Generate embeddings for each market question using Gemini API
-- 2. Update the embedding column with the vector values
-- Example update:
-- UPDATE markets SET embedding = '[0.123, 0.456, ...]'::vector WHERE market_id = '...';
