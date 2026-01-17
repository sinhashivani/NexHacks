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
├── docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── SUPABASE_SETUP.md         # Supabase setup guide
│   ├── DATABASE_SCHEMA.md        # Database schema
│   ├── IMPLEMENTATION_GUIDE.md   # Code examples
│   └── QUICK_REFERENCE.md        # Quick reference
├── database/                      # Database code
│   ├── supabase_connection.py   # Supabase connection handler
│   ├── schema.sql                # Database schema SQL
│   ├── test_connection.py        # Connection test script
│   └── init_db.py                # Database initialization check
├── Polymarket API/                # API integration scripts
└── polymarket_events_by_tags.csv # Market data
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
pip install supabase python-dotenv requests pandas
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

### 5. Test Connection

```bash
python database/test_connection.py
```

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
3. ⏳ Import Polymarket CSV data
4. ⏳ Build correlation algorithms
5. ⏳ Create API endpoints
6. ⏳ Build frontend tables (Related Trades, Correlated Trades)