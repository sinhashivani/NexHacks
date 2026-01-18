# Database Migration Checklist

Run these in order. **SQL** = run in Supabase Dashboard → SQL Editor. **Python** = run in terminal from project root.

---

## Prerequisites

- **Supabase** project with `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
- **`update_updated_at_column` function** (needed by 003): if 003 fails on the trigger, run this in SQL Editor first:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

---

## 1. Base schema (if starting from scratch)

If your DB has no `markets` table, run **`database/schema.sql`** in the SQL Editor first.  
If you already have `markets` and `parlay_suggestions`, skip this.

---

## 2. SQL migrations (Supabase SQL Editor)

| # | File | What it does | When to run |
|---|------|--------------|-------------|
| **002** | `database/migrations/002_drop_unused_tables.sql` | Drops `hedge_opportunities`, `trade_correlations`, `related_trades`, `user_trades` | Only if you want to remove those tables (e.g. before recreating `related_trades` with 006) |
| **003** | `database/migrations/003_create_market_metrics.sql` | Creates `market_metrics` | Before using trending / refresh |
| **004** | `database/migrations/004_create_similarity_table.sql` | Adds `event_title` to `markets`, creates `similarity_scores` | Before similarity and 005 |
| **006** | `database/migrations/006_create_related_trades_table.sql` | Creates `related_trades` | After 002 if you dropped it, or if the table doesn’t exist |

---

## 3. Python migrations / scripts (terminal)

| # | Command | What it does | Needs |
|---|---------|--------------|-------|
| **001** | `python database/migrations/001_import_markets_from_csv_simple.py` | Imports markets from CSV into `markets` | `markets` table, `data/polymarket_events_by_tags.csv` |
| **004i** | `python database/migrations/004_import_similarity_scores.py` | Imports similarity data into `similarity_scores` | `similarity_scores` table (004), `similarity_scores.csv` in project root |
| **005** | `python database/migrations/005_update_markets_with_event_title.py` | Backfills `event_title` in `markets` from CSV | `markets.event_title` (004), `data/polymarket_events_by_tags.csv` |
| **populate** | `python scripts/populate_related_trades.py` | Fills `related_trades` with event + sector relationships | `related_trades` table (006) |

---

## 4. Generating `similarity_scores.csv` (if missing)

`004_import_similarity_scores` expects `similarity_scores.csv` in the project root (or pass `--csv path/to/similarity_scores.csv`).

To generate it:

```bash
# From project root. Edit scripts/get_similarity_scores.py INPUT_CSV to "data/polymarket_events_by_tags.csv" if needed, then:
python scripts/get_similarity_scores.py
# Puts similarity_scores.csv in project root
```

---

## 5. Suggested order (first-time setup)

1. **003** – `003_create_market_metrics.sql` (SQL)  
2. **004** – `004_create_similarity_table.sql` (SQL)  
3. **006** – `006_create_related_trades_table.sql` (SQL)  
4. **001** – `001_import_markets_from_csv_simple.py` (Python) — if you need to (re)import markets  
5. **004i** – `004_import_similarity_scores.py` (Python) — after `similarity_scores.csv` exists  
6. **005** – `005_update_markets_with_event_title.py` (Python)  
7. **populate** – `scripts/populate_related_trades.py` (Python)  

**002** – Run only if you explicitly want to drop `user_trades`, `trade_correlations`, `related_trades`, `hedge_opportunities`. If you run 002, run **006** afterward to recreate `related_trades`.

---

## 6. What’s likely already done (from your setup)

- **markets** – populated  
- **market_metrics** – exists (e.g. 30 rows from refresh)  
- **event_title** – column exists (004); 005 has been run to backfill  
- **similarity_scores** – table exists; 004_import may or may not have been run  
- **related_trades** – table exists (006); `populate_related_trades` has been run  

---

## 7. Still to run (check against your DB)

Use this as a checklist. For each, confirm in Supabase (Table Editor or `information_schema`) or by running the script:

| Task | How to check | Run if missing |
|------|--------------|----------------|
| **003 – market_metrics** | Table `market_metrics` exists | `003_create_market_metrics.sql` |
| **004 – similarity schema** | `markets.event_title` exists and `similarity_scores` exists | `004_create_similarity_table.sql` |
| **006 – related_trades** | Table `related_trades` exists | `006_create_related_trades_table.sql` |
| **004i – similarity data** | `similarity_scores` has rows | `004_import_similarity_scores.py` (and `similarity_scores.csv`) |
| **005 – event_title backfill** | `markets` has non-null `event_title` for many rows | `005_update_markets_with_event_title.py` |
| **populate – related_trades data** | `related_trades` has rows | `scripts/populate_related_trades.py` |

---

## 8. One-off: only run 002 if you need a clean slate

**002_drop_unused_tables.sql** removes:

- `hedge_opportunities`
- `trade_correlations`
- `related_trades`
- `user_trades`

Run 002 only when you intend to drop these. After 002, run **006** to recreate `related_trades`, then `scripts/populate_related_trades.py` to fill it.
