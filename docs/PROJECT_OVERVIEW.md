# NexHacks - Polymarket Correlation Tool

## Project Overview

We are building a tool to help Polymarket users identify correlated trades, find parlay opportunities, and discover hedge options. Polymarket is a prediction market platform, but it doesn't currently help users identify similar or correlated trades. Our tool fills this gap.

## Problem Statement

Polymarket lacks features to help users:
- Identify similarly correlated trades based on title text and other inputs
- Place "parlay" style trades to leverage and amplify returns
- Identify hedge opportunities per trade
- Prevent contradictory trades (e.g., if you pick a team to win, you can't also select the under)

## Solution

We're building additional software that:

1. **Identifies Correlated Trades**: Uses title text similarity and other inputs to find correlated markets
2. **Suggests Parlay Combinations**: Recommends multiple correlated trades to amplify returns
3. **Identifies Hedge Opportunities**: Finds inverse correlations to help users hedge their positions
4. **Prevents Contradictory Trades**: Blocks users from selecting conflicting outcomes

## Features

### Frontend (To Be Built)
- **Table 1: Related Trades** - Shows strictly related markets (pairs trading)
- **Table 2: Correlated Trades** - Shows 2+ related trades with correlation metrics and timeline
- **Table 3: Inversely Related Trades** (Optional) - Shows inverse correlations for hedging

Each table will:
- Show the original trade
- Make recommendations based on what the user already traded on
- Check across categories and metrics
- Display correlation scores and relationship strength

### Backend
- Correlation calculation algorithms
- Text similarity analysis
- Price correlation analysis
- Parlay suggestion engine
- Hedge opportunity finder

## Tech Stack

- **Database**: Supabase (PostgreSQL)
- **Backend**: Python
- **Frontend**: (To be determined)
- **APIs**: Polymarket Gamma API

## Database Structure

### Current Tables

1. **`markets`** - Stores all Polymarket market data
   - Fields: `market_id`, `market_slug`, `question`, `tag_label`, `tag_id`, `clob_token_ids`, `active`, `closed`
   - Contains ~5,770 markets imported from Polymarket API

2. **`parlay_suggestions`** - Stores suggested parlay combinations
   - Fields: `user_id`, `base_market_id`, `suggested_markets` (JSONB), `expected_return`, `risk_level`, `confidence`
   - Links to markets table via `base_market_id`

### Removed Tables (Simplified Schema)
- `user_trades` - Removed (not needed for MVP)
- `trade_correlations` - Will be calculated on-the-fly or stored differently
- `related_trades` - Will be calculated on-the-fly
- `hedge_opportunities` - Will be calculated on-the-fly

## Data Source

- **Polymarket Gamma API**: https://gamma-api.polymarket.com
- **Categories**: finance, politics, elections, tech, economy
- **Current Data**: 8,768 market records imported from CSV
- **Active Markets**: Only active, non-closed markets are stored

## Team Roles

- **Shivani**: Back End, Front End
- **Nicolas**: Back End
- **Shilo**: Database Management, Supabase Setup
- **Arav**: Business Logic, Pitch Deck, Front End

## Current Status

### ✅ Completed
- Supabase database setup and configuration
- Database schema creation (markets, parlay_suggestions tables)
- CSV data import (8,768 markets imported)
- Database connection module
- Migration scripts for data import
- Project documentation

### 🚧 In Progress / To Do
- Correlation calculation algorithms
- Text similarity analysis
- Price correlation analysis
- API endpoints for frontend
- Frontend tables (Related Trades, Correlated Trades)
- Parlay suggestion algorithm
- Hedge opportunity finder
- User interface

## Key Algorithms Needed

1. **Text Similarity**: Compare market questions/titles to find similar markets
   - Use NLP techniques (TF-IDF, cosine similarity, embeddings)
   - Consider category/tag matching

2. **Price Correlation**: Analyze historical price movements
   - Calculate correlation coefficients between market prices
   - Identify positive, negative, and neutral correlations

3. **Parlay Suggestion**: Combine correlated markets
   - Find markets with high positive correlation
   - Calculate expected return multipliers
   - Assess risk levels

4. **Hedge Identification**: Find inverse correlations
   - Identify markets with negative correlation
   - Calculate hedge ratios
   - Estimate risk reduction

## Database Connection

- **Platform**: Supabase (PostgreSQL)
- **Connection**: Via Supabase Python client
- **Credentials**: Stored in `.env` file (not committed to git)
- **Connection Module**: `database/supabase_connection.py`

## Project Structure

```
NexHacks/
├── database/
│   ├── supabase_connection.py      # Database connection handler
│   ├── schema.sql                  # Database schema
│   └── migrations/
│       ├── 001_import_markets_from_csv_simple.py  # Data import script
│       └── 002_drop_unused_tables.sql            # Schema cleanup
├── docs/
│   ├── PROJECT_OVERVIEW.md        # This file
│   ├── SUPABASE_SETUP.md          # Database setup guide
│   └── ...                        # Other documentation
├── Polymarket API/
│   └── get_event_data.py          # API integration (groupmate's code)
├── polymarket_events_by_tags.csv  # Market data (8,768 rows)
└── .env                           # Environment variables (not committed)
```

## Next Steps

1. **Build Correlation Algorithms**
   - Text similarity using market questions
   - Price correlation analysis
   - Category-based relationships

2. **Create API Endpoints**
   - GET /markets - List all markets
   - GET /markets/{id}/related - Get related trades
   - GET /markets/{id}/correlated - Get correlated trades
   - GET /markets/{id}/parlay-suggestions - Get parlay suggestions
   - GET /markets/{id}/hedge-opportunities - Get hedge opportunities

3. **Build Frontend**
   - Display tables for related/correlated trades
   - Show correlation metrics
   - Allow users to select trades
   - Prevent contradictory selections

4. **Implement Business Logic**
   - Parlay calculation
   - Risk assessment
   - Return estimation

## Key Metrics to Display

- **Correlation Score**: -1 to 1 (how correlated two markets are)
- **Similarity Score**: 0 to 1 (text similarity)
- **Price Correlation**: -1 to 1 (price movement correlation)
- **Expected Return**: Multiplier for parlay combinations
- **Risk Level**: Low, Medium, High
- **Confidence**: 0 to 1 (confidence in suggestion)

## Constraints & Requirements

- Must work with Polymarket's existing API
- Cannot modify Polymarket's platform
- Must be a separate tool/extension
- Should provide real-time or near-real-time suggestions
- Must handle large datasets (thousands of markets)
- Should be performant for user experience

## Success Criteria

- Users can identify correlated trades easily
- Users can build parlay combinations with confidence
- Users can find hedge opportunities
- System prevents contradictory trade selections
- Recommendations are accurate and useful
- Interface is intuitive and fast

---

**Last Updated**: Current session
**Status**: Database setup complete, ready for algorithm development
