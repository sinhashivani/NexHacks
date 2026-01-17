# Project Structure

## Directory Layout

```
NexHacks/
├── api.py                          # FastAPI application (main entry point)
├── README.md                       # Project README
├── .cursorrules                    # Cursor AI context and rules
├── .env                            # Environment variables (not committed)
├── .gitignore                      # Git ignore rules
│
├── database/                       # Database layer
│   ├── __init__.py
│   ├── supabase_connection.py      # Supabase connection handler
│   ├── schema.sql                  # Database schema
│   └── migrations/                 # Database migrations
│       ├── __init__.py
│       ├── 001_import_markets_from_csv_simple.py
│       ├── 002_drop_unused_tables.sql
│       └── 003_create_market_metrics.sql
│
├── services/                       # Business logic services
│   ├── __init__.py
│   ├── trending.py                 # Trending markets service
│   └── polymarket_api.py           # Polymarket API integration service
│
├── polymarket/                     # Polymarket API integration
│   ├── __init__.py
│   ├── get_markets_data.py         # Market data fetching
│   ├── get_event_data.py           # Event data fetching
│   └── get_similarity_scores.py    # Similarity calculations
│
├── data/                           # Data files
│   └── polymarket_events_by_tags.csv  # Market data CSV
│
└── docs/                          # Documentation
    ├── README.md                   # Documentation index
    ├── PROJECT_OVERVIEW.md         # Project overview
    ├── SUPABASE_SETUP.md           # Supabase setup guide
    ├── API_ENDPOINTS.md             # API documentation
    ├── DATABASE_SCHEMA.md           # Database schema docs
    ├── IMPLEMENTATION_GUIDE.md      # Implementation guide
    ├── QUICK_REFERENCE.md           # Quick reference
    └── QUICK_START.md              # Quick start guide
```

## Key Files

### API & Application
- **`api.py`** - Main FastAPI application with all endpoints
- **`.cursorrules`** - Cursor AI context for project understanding

### Database
- **`database/supabase_connection.py`** - Database connection handler
- **`database/schema.sql`** - Complete database schema
- **`database/migrations/`** - Database migration scripts

### Services
- **`services/trending.py`** - Trending markets calculation
- **`services/polymarket_api.py`** - Polymarket API wrapper

### Integrations
- **`polymarket/get_markets_data.py`** - Market data fetching
- **`polymarket/get_event_data.py`** - Event data fetching

### Data
- **`data/polymarket_events_by_tags.csv`** - Market data (8,768 markets)

## Running the Application

```bash
# Start FastAPI server
uvicorn api:app --reload

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

## Import Paths

When importing modules, use:
- `from database.supabase_connection import SupabaseConnection`
- `from services.trending import TrendingService`
- `from polymarket.get_markets_data import ui, mid`
- `from services.polymarket_api import PolymarketAPIService`
