# Quick Start: Similarity System

## 5-Minute Setup Guide

### Prerequisites
- Supabase project configured
- Markets table populated
- `similarity_scores.csv` file in project root
- `data/polymarket_events_by_tags.csv` file available

### Step 1: Create Database Tables (2 minutes)

1. Open Supabase Dashboard → SQL Editor
2. Copy and paste contents of `database/migrations/004_create_similarity_table.sql`
3. Click "Run"

**Verify:**
- Check that `similarity_scores` table exists
- Check that `markets` table has `event_title` column

### Step 2: Import Similarity Scores (1-2 minutes)

```bash
python database/migrations/004_import_similarity_scores.py
```

**Expected:** Shows progress and final count of imported scores

### Step 3: Update Markets with Event Titles (1 minute)

```bash
python database/migrations/005_update_markets_with_event_title.py
```

**Expected:** Shows number of markets updated

### Step 4: Test It! (30 seconds)

```bash
python scripts/test_similar_markets.py
```

**Expected:** Shows test results with similar markets found

### Step 5: Use the API

```bash
# Start API server
uvicorn api.main:app --reload

# Test endpoint
curl "http://localhost:8000/similar?event_title=MicroStrategy sells any Bitcoin by ___ ?"
```

## Common Commands

### Import Similarity Scores
```bash
python database/migrations/004_import_similarity_scores.py
```

### Update Event Titles
```bash
python database/migrations/005_update_markets_with_event_title.py
```

### Run Tests
```bash
python scripts/test_similar_markets.py
```

### Test API Endpoint
```bash
curl "http://localhost:8000/similar?event_title=YOUR_EVENT_TITLE"
```

## Troubleshooting

### "No similar markets found"
- Check if similarity scores were imported: `SELECT COUNT(*) FROM similarity_scores;`
- Check if event titles exist: `SELECT DISTINCT event_title FROM markets LIMIT 10;`
- Run test script to diagnose: `python scripts/test_similar_markets.py`

### "Table doesn't exist"
- Run migration SQL: `database/migrations/004_create_similarity_table.sql`
- Check Supabase dashboard for table creation

### "CSV file not found"
- Ensure `similarity_scores.csv` is in project root
- Or specify path: `python database/migrations/004_import_similarity_scores.py --csv /path/to/file.csv`

## Next Steps

- Read full documentation: `docs/SIMILARITY_SYSTEM.md`
- See all changes: `docs/CHANGELOG_SIMILARITY.md`
- API documentation: `docs/API_ENDPOINTS.md`
