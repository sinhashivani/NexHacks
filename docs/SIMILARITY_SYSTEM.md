# Similarity System Implementation

## Overview

The similarity system allows users to find markets similar to a given event based on cosine similarity scores calculated from market question text. This enables discovery of related trading opportunities and correlated markets.

## Architecture

### Components

1. **Similarity Scores Table** - Stores pre-calculated cosine similarity scores between markets
2. **Event Title Mapping** - Links markets to their event titles for easier querying
3. **Similar Markets Function** - Queries and returns top similar markets with metadata

### Data Flow

```
Event Title → Markets Table (get clob_token_ids)
           → Similarity Scores Table (find similar token IDs)
           → Markets Table (enrich with metadata)
           → Return Top 5 Similar Markets
```

## Database Schema

### New Tables

#### `similarity_scores`
Stores cosine similarity scores between market pairs.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `source_clob_token_ids` | TEXT | Source market's token IDs (normalized JSON) |
| `neighbor_clob_token_ids` | TEXT | Similar market's token IDs (normalized JSON) |
| `cosine_similarity` | NUMERIC(10,8) | Similarity score (0-1) |
| `created_at` | TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_similarity_source` - Fast lookup by source token IDs
- `idx_similarity_neighbor` - Fast lookup by neighbor token IDs
- `idx_similarity_score` - Sorting by similarity score
- `idx_similarity_source_score` - Composite index for optimized queries

### Modified Tables

#### `markets`
Added `event_title` column to enable querying by event.

| Column | Type | Description |
|--------|------|-------------|
| `event_title` | TEXT | Event title that groups related markets |

**Index:**
- `idx_markets_event_title` - Fast lookup by event title

## Implementation Files

### 1. Database Migrations

#### `004_create_similarity_table.sql`
- Creates `similarity_scores` table
- Adds `event_title` column to `markets` table
- Creates necessary indexes

**Usage:**
```sql
-- Run in Supabase SQL Editor
-- Copy contents from database/migrations/004_create_similarity_table.sql
```

#### `004_import_similarity_scores.py`
- Imports similarity scores from `similarity_scores.csv`
- Normalizes token IDs for consistent matching
- Batch inserts for performance

**Usage:**
```bash
python database/migrations/004_import_similarity_scores.py
# Or with custom CSV path:
python database/migrations/004_import_similarity_scores.py --csv path/to/similarity_scores.csv
```

#### `005_update_markets_with_event_title.py`
- Updates existing markets with `event_title` from CSV
- Matches markets by `clob_token_ids`
- Useful for backfilling event titles

**Usage:**
```bash
python database/migrations/005_update_markets_with_event_title.py
# Or with custom CSV path:
python database/migrations/005_update_markets_with_event_title.py --csv data/polymarket_events_by_tags.csv
```

### 2. Core Function

#### `polymarket/get_similar_markets.py`

**Function:** `get_similar_by_event_title(event_title: str, limit: int = 5) -> dict`

**Process:**
1. Query `markets` table for all markets with matching `event_title`
2. Extract and normalize `clob_token_ids` from found markets
3. Query `similarity_scores` table for similar markets using source token IDs
4. Sort by `cosine_similarity` (descending) and get top N results
5. Enrich results by querying `markets` table for full market metadata
6. Return structured response with similar markets

**Response Format:**
```python
{
    "event_title": str,
    "clob_token_ids": List[str],  # Token IDs for this event
    "event_markets": List[dict],   # Markets belonging to this event
    "similar_markets": List[dict], # Top similar markets
    "count": int                   # Number of similar markets found
}
```

**Similar Market Object:**
```python
{
    "market_id": str,
    "question": str,
    "market_slug": str,
    "event_title": str,
    "tag_label": str,
    "clob_token_ids": str,
    "cosine_similarity": float
}
```

### 3. API Integration

#### `api/main.py`

**Endpoint:** `GET /similar?event_title={event_title}`

**Query Parameters:**
- `event_title` (required): Exact event title to search for

**Response:**
```json
{
    "event_title": "MicroStrategy sells any Bitcoin by ___ ?",
    "clob_token_ids": ["[...]"],
    "event_markets": [...],
    "similar_markets": [
        {
            "market_id": "123",
            "question": "Will Bitcoin price exceed $100k?",
            "cosine_similarity": 0.8735,
            ...
        }
    ],
    "count": 5
}
```

## Setup Instructions

### Step 1: Run Database Migration

1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `database/migrations/004_create_similarity_table.sql`
3. Execute the SQL

### Step 2: Import Similarity Scores

```bash
# Make sure similarity_scores.csv exists in project root
python database/migrations/004_import_similarity_scores.py
```

**Expected Output:**
- Processes similarity scores from CSV
- Inserts into `similarity_scores` table
- Shows progress and final count

### Step 3: Update Markets with Event Titles

```bash
# Update existing markets with event_title from CSV
python database/migrations/005_update_markets_with_event_title.py
```

**Expected Output:**
- Reads `data/polymarket_events_by_tags.csv`
- Updates markets table with event_title
- Shows number of markets updated

### Step 4: Test the System

```bash
# Run test script
python scripts/test_similar_markets.py
```

## Testing

### Test Script: `scripts/test_similar_markets.py`

The test script performs:

1. **Database Connection Test**
   - Verifies connection to Supabase
   - Checks table accessibility
   - Validates schema

2. **Event Title Discovery**
   - Finds available event titles in database
   - Lists sample titles for testing

3. **Single Event Test**
   - Tests `get_similar_by_event_title` with one event
   - Shows detailed results including:
     - Event markets found
     - Similar markets with similarity scores
     - Market metadata

4. **Multiple Event Test**
   - Tests multiple event titles
   - Provides summary statistics

5. **Error Handling Test**
   - Tests with non-existent event titles
   - Verifies graceful error handling

**Usage:**
```bash
python scripts/test_similar_markets.py
```

## Data Requirements

### Input Files

1. **`similarity_scores.csv`**
   - Format: `source_clob_token_ids, neighbor_clob_token_ids, cosine_similarity`
   - Generated by `scripts/get_similarity_scores.py`
   - Contains pre-calculated similarity scores

2. **`data/polymarket_events_by_tags.csv`**
   - Format: `event_title, market_question, clob_token_ids`
   - Used to map markets to event titles
   - Source for event_title backfill

### Token ID Normalization

Token IDs are normalized for consistent matching:
- Parsed as JSON arrays
- Sorted and deduplicated
- Re-serialized with compact formatting
- This ensures matching works even if token IDs are stored in different formats

## Performance Considerations

### Indexes

The following indexes optimize query performance:

1. **`idx_similarity_source`** - Fast lookup of similarities by source
2. **`idx_similarity_source_score`** - Composite index for sorted queries
3. **`idx_markets_event_title`** - Fast lookup of markets by event title
4. **`idx_markets_clob_token_ids`** - Fast lookup for enrichment queries

### Query Optimization

- Batch processing for multiple token IDs
- Limit queries to top N results early
- Deduplication to avoid processing same markets multiple times
- Efficient joins using indexed columns

## Limitations

1. **Exact Match Required**: Event title must match exactly (case-sensitive)
2. **Token ID Matching**: Relies on normalized token ID strings matching exactly
3. **Pre-calculated Scores**: Similarity scores must be pre-calculated and imported
4. **No Real-time Calculation**: Similarity is not calculated on-the-fly

## Future Enhancements

1. **Fuzzy Matching**: Support partial/approximate event title matching
2. **Real-time Similarity**: Calculate similarity on-the-fly using embeddings
3. **Multiple Similarity Metrics**: Support different similarity algorithms
4. **Caching**: Cache results for frequently queried event titles
5. **Pagination**: Support pagination for large result sets

## Troubleshooting

### No Similar Markets Found

**Possible Causes:**
1. Similarity scores not imported
2. Event title doesn't exist in database
3. No markets match the token IDs in similarity table
4. Token ID normalization mismatch

**Solutions:**
- Run `004_import_similarity_scores.py` migration
- Run `005_update_markets_with_event_title.py` migration
- Check token ID format matches between tables
- Verify similarity_scores.csv exists and is valid

### Slow Queries

**Possible Causes:**
1. Missing indexes
2. Large result sets
3. Inefficient queries

**Solutions:**
- Verify all indexes are created
- Reduce limit parameter
- Check query execution plans in Supabase

### Token ID Mismatches

**Possible Causes:**
1. Different normalization formats
2. Missing or malformed token IDs

**Solutions:**
- Ensure `normalize_token_ids` function is used consistently
- Verify CSV data format matches expected structure
- Check for null or empty token IDs

## Related Files

- `scripts/get_similarity_scores.py` - Generates similarity_scores.csv
- `scripts/get_event_data.py` - Generates polymarket_events_by_tags.csv
- `api/main.py` - API endpoint integration
- `database/schema.sql` - Full database schema

## API Documentation

See `docs/API_ENDPOINTS.md` for complete API documentation including the `/similar` endpoint.
