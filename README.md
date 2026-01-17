# NexHacks - Polymarket Correlation Tool

A tool to help Polymarket users identify correlated trades, find parlay opportunities, and discover hedge options.

## Features

- **Related Trades**: Identify strictly related markets (pairs trading)
- **Correlated Trades**: Find markets with statistical correlation + timeline
- **Parlay Suggestions**: Amplify returns through correlated trade combinations
- **Hedge Opportunities**: Identify inverse correlations to reduce risk

## Project Structure

```
NexHacks/
├── api.py                         # FastAPI application (main entry point)
├── database/                      # Database layer
│   ├── supabase_connection.py     # Supabase connection handler
│   ├── schema.sql                 # Database schema SQL
│   └── migrations/                # Database migrations
├── services/                       # Business logic services
│   ├── trending.py                # Trending markets service
│   └── polymarket_api.py          # Polymarket API service
├── polymarket/                    # Polymarket API integration
│   ├── get_markets_data.py        # Market data fetching
│   └── get_event_data.py         # Event data fetching
├── data/                          # Data files
│   └── polymarket_events_by_tags.csv
└── docs/                          # Documentation
    ├── PROJECT_OVERVIEW.md         # Project overview
    ├── SUPABASE_SETUP.md          # Supabase setup guide
    ├── API_ENDPOINTS.md           # API documentation
    └── ...
```

## Quick Start

### 1. Supabase Setup

**For database setup and Supabase configuration, see the complete documentation:**

📚 **[Supabase Setup Guide](./docs/SUPABASE_SETUP.md)**

Quick steps:
1. Create account at [supabase.com](https://supabase.com)
2. Create a new project (Free tier)
3. Get your Project URL and anon key from Settings → API
4. Add to `.env` file (see below)

### 2. Install Dependencies

```bash
pip install fastapi uvicorn supabase python-dotenv requests
```

### 3. Configure Environment

Create a `.env` file:
```env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_NAME=nexhacks_polymarket
```

### 4. Create Database Schema

1. Go to Supabase dashboard → SQL Editor
2. Copy contents of `database/schema.sql`
3. Paste and run in SQL Editor

### 5. Start the API Server

```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Trending Markets: `http://localhost:8000/markets/trending`

## Team Roles

- **Shivani**: Back End, Front End
- **Nicolas**: Back End
- **Shilo**: Database Management, Supabase
- **Arav**: Business Logic, Pitch Deck, Front End

## Documentation

All documentation is in the [`docs/`](./docs/) directory:

- **[Supabase Setup Guide](./docs/SUPABASE_SETUP.md)** - Complete setup instructions
- **[Database Schema](./docs/DATABASE_SCHEMA.md)** - Table structures and relationships
- **[Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md)** - Code examples and patterns
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Common operations cheat sheet

## Next Steps

1. ✅ Set up Supabase (see [SUPABASE_SETUP.md](./docs/SUPABASE_SETUP.md))
2. ✅ Run database schema SQL
3. ✅ Import Polymarket CSV data
4. ✅ Trending markets endpoint implemented
5. ⏳ Build correlation algorithms
6. ⏳ Build frontend tables (Related Trades, Correlated Trades)

## Quick Start

See [QUICK_START.md](./docs/QUICK_START.md) for detailed setup instructions.

## API Endpoints

- `GET /markets/trending` - Get trending/popular markets
- `GET /markets/trending/refresh` - Refresh market metrics from Polymarket
- `GET /ui?token_id=...` - Get market UI data

See [API_ENDPOINTS.md](./docs/API_ENDPOINTS.md) for complete API documentation.