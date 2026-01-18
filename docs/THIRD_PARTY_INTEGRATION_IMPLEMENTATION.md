# Third-Party Integration Implementation Guide

## Overview

This guide implements the strategy to embed Polymarket prediction markets into third-party platforms (sports betting, crypto wallets, financial platforms) to create a unified parlay intelligence layer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NexHacks API Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Polymarket   │  │ Correlation  │  │ Parlay       │      │
│  │ Data         │  │ Engine       │  │ Calculator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ The Odds API │  │ MetaMask     │  │ Zapier       │
│ (Sports)     │  │ Snap         │  │ Webhooks     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Tier 1: MVP Integrations (Week 1-2)

### 1. The Odds API Integration

#### Purpose
Show correlation between Polymarket prediction markets and sports betting odds, enabling cross-platform parlay suggestions.

#### Implementation Steps

##### Step 1: Create Service Layer

**File:** `services/odds_api.py`

```python
"""
The Odds API Service
Fetches sports betting odds and correlates with Polymarket markets
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class OddsAPIService:
    """Service for fetching sports betting odds from The Odds API"""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self):
        self.api_key = os.getenv("THE_ODDS_API_KEY")
        if not self.api_key:
            raise ValueError("THE_ODDS_API_KEY not found in environment variables")
        self.timeout = 10
    
    def get_sports(self) -> List[Dict]:
        """Get list of available sports"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/sports",
                params={"apiKey": self.api_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching sports: {e}")
            return []
    
    def get_odds(
        self,
        sport: str,
        regions: str = "us",
        markets: str = "h2h",
        odds_format: str = "american"
    ) -> List[Dict]:
        """
        Get odds for a specific sport
        
        Args:
            sport: Sport key (e.g., 'americanfootball_nfl', 'basketball_nba')
            regions: Comma-separated regions (us, uk, au)
            markets: Comma-separated markets (h2h, spreads, totals)
            odds_format: american, decimal, or fractional
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/sports/{sport}/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": regions,
                    "markets": markets,
                    "oddsFormat": odds_format
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching odds: {e}")
            return []
    
    def get_upcoming_games(self, sport: str, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming games for a sport"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/sports/{sport}/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": "us",
                    "markets": "h2h",
                    "oddsFormat": "decimal"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            games = response.json()
            
            # Filter for upcoming games
            now = datetime.utcnow()
            cutoff = now + timedelta(days=days_ahead)
            
            upcoming = []
            for game in games:
                commence_time = datetime.fromisoformat(game.get("commence_time", "").replace("Z", "+00:00"))
                if now < commence_time < cutoff:
                    upcoming.append(game)
            
            return upcoming
        except Exception as e:
            print(f"Error fetching upcoming games: {e}")
            return []
```

##### Step 2: Create Correlation Engine

**File:** `services/correlation_engine.py`

```python
"""
Correlation Engine
Matches Polymarket markets with sports betting odds
"""

from typing import List, Dict, Optional
from services.odds_api import OddsAPIService
from database.supabase_connection import SupabaseConnection
import re
from difflib import SequenceMatcher

class CorrelationEngine:
    """Matches Polymarket markets with sports betting odds"""
    
    def __init__(self):
        self.odds_service = OddsAPIService()
        self.db = SupabaseConnection()
    
    def extract_team_names(self, text: str) -> List[str]:
        """Extract team names from text using common patterns"""
        # Common team name patterns
        nfl_teams = [
            "Chiefs", "Bills", "Dolphins", "Patriots", "Jets",
            "Ravens", "Bengals", "Browns", "Steelers",
            "Texans", "Colts", "Jaguars", "Titans",
            "Broncos", "Chargers", "Raiders", "Cowboys",
            "Giants", "Eagles", "Commanders", "Packers",
            "Vikings", "Bears", "Lions", "Falcons",
            "Panthers", "Saints", "Buccaneers", "Cardinals",
            "Rams", "49ers", "Seahawks"
        ]
        
        found_teams = []
        text_lower = text.lower()
        
        for team in nfl_teams:
            if team.lower() in text_lower:
                found_teams.append(team)
        
        return found_teams
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def find_correlated_markets(
        self,
        polymarket_question: str,
        sport: str = "americanfootball_nfl"
    ) -> List[Dict]:
        """
        Find sports betting odds that correlate with a Polymarket market
        
        Args:
            polymarket_question: The Polymarket market question
            sport: Sport to search in
        
        Returns:
            List of correlated betting opportunities
        """
        # Extract team names from Polymarket question
        teams = self.extract_team_names(polymarket_question)
        
        if not teams:
            return []
        
        # Get upcoming games
        games = self.odds_service.get_upcoming_games(sport)
        
        correlations = []
        
        for game in games:
            home_team = game.get("home_team", "")
            away_team = game.get("away_team", "")
            
            # Check if any extracted teams match
            match_score = 0
            matched_teams = []
            
            for team in teams:
                if team in home_team or team in away_team:
                    match_score += 1
                    matched_teams.append(team)
            
            if match_score > 0:
                # Calculate overall similarity
                game_text = f"{away_team} vs {home_team}"
                similarity = self.calculate_text_similarity(
                    polymarket_question,
                    game_text
                )
                
                # Get best odds
                best_odds = self._get_best_odds(game)
                
                correlations.append({
                    "game": game,
                    "matched_teams": matched_teams,
                    "similarity_score": similarity,
                    "match_score": match_score,
                    "odds": best_odds,
                    "correlation_strength": min(similarity * match_score, 1.0)
                })
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: x["correlation_strength"], reverse=True)
        
        return correlations[:5]  # Top 5
    
    def _get_best_odds(self, game: Dict) -> Dict:
        """Extract best odds from game data"""
        best_odds = {}
        
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":  # Head to head
                    for outcome in market.get("outcomes", []):
                        team = outcome.get("name")
                        price = outcome.get("price")
                        
                        if team and price:
                            if team not in best_odds or price > best_odds[team]["price"]:
                                best_odds[team] = {
                                    "price": price,
                                    "bookmaker": bookmaker.get("title")
                                }
        
        return best_odds
```

##### Step 3: Create Database Schema

**File:** `database/migrations/006_create_odds_correlation.sql`

```sql
-- Migration: Create Odds Correlation Tables
-- Stores correlations between Polymarket markets and sports betting odds

-- Table to store sports betting odds
CREATE TABLE IF NOT EXISTS sports_odds (
    id BIGSERIAL PRIMARY KEY,
    sport_key TEXT NOT NULL,
    game_id TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    commence_time TIMESTAMP WITH TIME ZONE NOT NULL,
    bookmaker TEXT NOT NULL,
    market_type TEXT NOT NULL,
    outcome_name TEXT NOT NULL,
    odds DECIMAL(10, 4) NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(game_id, bookmaker, market_type, outcome_name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sports_odds_sport ON sports_odds(sport_key);
CREATE INDEX IF NOT EXISTS idx_sports_odds_commence_time ON sports_odds(commence_time);
CREATE INDEX IF NOT EXISTS idx_sports_odds_teams ON sports_odds(home_team, away_team);

-- Table to store correlations
CREATE TABLE IF NOT EXISTS odds_correlations (
    id BIGSERIAL PRIMARY KEY,
    market_id TEXT NOT NULL REFERENCES markets(market_id),
    game_id TEXT NOT NULL,
    correlation_score DECIMAL(5, 4) NOT NULL CHECK (correlation_score >= 0 AND correlation_score <= 1),
    matched_teams TEXT[],
    similarity_score DECIMAL(5, 4),
    suggested_parlay JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(market_id, game_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_odds_correlations_market ON odds_correlations(market_id);
CREATE INDEX IF NOT EXISTS idx_odds_correlations_score ON odds_correlations(correlation_score DESC);
```

##### Step 4: Create API Endpoints

**File:** `api/main.py` (add these endpoints)

```python
from services.correlation_engine import CorrelationEngine
from services.odds_api import OddsAPIService

# Initialize services
correlation_engine = CorrelationEngine()
odds_service = OddsAPIService()

@app.get("/odds/sports")
def get_available_sports():
    """Get list of available sports from The Odds API"""
    try:
        sports = odds_service.get_sports()
        return {"sports": sports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odds/correlated")
def get_correlated_odds(
    market_id: str = Query(..., description="Polymarket market ID"),
    sport: str = Query("americanfootball_nfl", description="Sport key")
):
    """
    Get sports betting odds correlated with a Polymarket market
    """
    try:
        # Get market from database
        conn = SupabaseConnection()
        client = conn.get_client()
        
        market = client.table("markets").select("*").eq("market_id", market_id).limit(1).execute()
        
        if not market.data:
            raise HTTPException(status_code=404, detail="Market not found")
        
        market_question = market.data[0].get("question", "")
        
        # Find correlations
        correlations = correlation_engine.find_correlated_markets(market_question, sport)
        
        return {
            "market_id": market_id,
            "market_question": market_question,
            "correlations": correlations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/parlay/suggestions")
def get_parlay_suggestions(
    market_id: str = Query(..., description="Polymarket market ID"),
    sport: str = Query("americanfootball_nfl", description="Sport key")
):
    """
    Get suggested parlay combining Polymarket market with sports betting odds
    """
    try:
        # Get correlations
        correlations = get_correlated_odds(market_id, sport)
        
        if not correlations.get("correlations"):
            return {
                "market_id": market_id,
                "suggestions": [],
                "message": "No correlated betting opportunities found"
            }
        
        # Calculate parlay suggestions
        suggestions = []
        
        for corr in correlations["correlations"][:3]:  # Top 3
            game = corr["game"]
            odds = corr["odds"]
            
            # Calculate expected parlay return
            # This is simplified - you'd want actual Polymarket odds
            polymarket_odds = 0.5  # Placeholder - get from actual market
            sports_odds = list(odds.values())[0]["price"] if odds else 1.0
            
            parlay_odds = polymarket_odds * sports_odds
            expected_return = parlay_odds - 1.0
            
            suggestions.append({
                "game": {
                    "home_team": game.get("home_team"),
                    "away_team": game.get("away_team"),
                    "commence_time": game.get("commence_time")
                },
                "correlation_score": corr["correlation_strength"],
                "polymarket_market": correlations["market_question"],
                "sports_bet": list(odds.keys())[0] if odds else "N/A",
                "combined_odds": parlay_odds,
                "expected_return": expected_return,
                "confidence": corr["correlation_strength"]
            })
        
        return {
            "market_id": market_id,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

##### Step 5: Frontend Component

**File:** `frontend/components/CorrelatedOdds.tsx` (if using React)

```typescript
import React, { useState, useEffect } from 'react';

interface Correlation {
  game: {
    home_team: string;
    away_team: string;
    commence_time: string;
  };
  correlation_score: number;
  odds: Record<string, { price: number; bookmaker: string }>;
}

export const CorrelatedOdds: React.FC<{ marketId: string }> = ({ marketId }) => {
  const [correlations, setCorrelations] = useState<Correlation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/odds/correlated?market_id=${marketId}&sport=americanfootball_nfl`)
      .then(res => res.json())
      .then(data => {
        setCorrelations(data.correlations || []);
        setLoading(false);
      });
  }, [marketId]);

  if (loading) return <div>Loading correlations...</div>;

  return (
    <div className="correlated-odds">
      <h3>Correlated Sports Betting Opportunities</h3>
      {correlations.map((corr, idx) => (
        <div key={idx} className="correlation-card">
          <div className="game-info">
            <h4>{corr.game.away_team} vs {corr.game.home_team}</h4>
            <p>Correlation: {(corr.correlation_score * 100).toFixed(1)}%</p>
          </div>
          <div className="odds">
            {Object.entries(corr.odds).map(([team, odds]) => (
              <div key={team}>
                <span>{team}: {odds.price.toFixed(2)}</span>
                <span className="bookmaker">{odds.bookmaker}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 2. MetaMask Snap Integration

#### Purpose
Show Polymarket data and parlay suggestions directly in MetaMask wallet.

#### Implementation Steps

##### Step 1: Create Snap Manifest

**File:** `metamask-snap/snap.manifest.json`

```json
{
  "version": "1.0.0",
  "description": "NexHacks Polymarket Parlay Intelligence",
  "proposedName": "NexHacks Polymarket",
  "repository": {
    "type": "git",
    "url": "https://github.com/your-org/nexhacks-metamask-snap"
  },
  "source": {
    "shasum": "YOUR_SNAP_SHA256_HASH",
    "location": {
      "npm": {
        "filePath": "dist/bundle.js",
        "packageName": "nexhacks-metamask-snap",
        "registry": "https://registry.npmjs.org"
      }
    }
  },
  "initialPermissions": {
    "endowment:network-access": {},
    "snap_dialog": {},
    "snap_manageState": {}
  },
  "manifestVersion": "0.1"
}
```

##### Step 2: Create Snap Source

**File:** `metamask-snap/src/index.ts`

```typescript
import { OnRpcRequestHandler } from '@metamask/snaps-types';
import { panel, text, heading } from '@metamask/snaps-ui';

const API_BASE = 'https://your-api.com/api';

export const onRpcRequest: OnRpcRequestHandler = async ({ request }) => {
  switch (request.method) {
    case 'get_trending_markets':
      return await getTrendingMarkets();
    
    case 'get_parlay_suggestions':
      const { marketId } = request.params as { marketId: string };
      return await getParlaySuggestions(marketId);
    
    case 'get_correlated_odds':
      const { marketId: mId } = request.params as { marketId: string };
      return await getCorrelatedOdds(mId);
    
    default:
      throw new Error('Method not found');
  }
};

async function getTrendingMarkets() {
  try {
    const response = await fetch(`${API_BASE}/markets/trending?limit=5`);
    const data = await response.json();
    
    return snap.request({
      method: 'snap_dialog',
      params: {
        type: 'alert',
        content: panel([
          heading('Trending Markets'),
          ...data.markets.map((m: any) => 
            text(`${m.question}\nScore: ${m.trending_score.toFixed(2)}`)
          )
        ])
      }
    });
  } catch (error) {
    return { error: 'Failed to fetch trending markets' };
  }
}

async function getParlaySuggestions(marketId: string) {
  try {
    const response = await fetch(`${API_BASE}/parlay/suggestions?market_id=${marketId}`);
    const data = await response.json();
    
    if (!data.suggestions || data.suggestions.length === 0) {
      return { message: 'No parlay suggestions available' };
    }
    
    const suggestions = data.suggestions.map((s: any) => 
      `${s.game.away_team} vs ${s.game.home_team}\nExpected Return: ${(s.expected_return * 100).toFixed(1)}%`
    ).join('\n\n');
    
    return snap.request({
      method: 'snap_dialog',
      params: {
        type: 'alert',
        content: panel([
          heading('Parlay Suggestions'),
          text(suggestions)
        ])
      }
    });
  } catch (error) {
    return { error: 'Failed to fetch parlay suggestions' };
  }
}

async function getCorrelatedOdds(marketId: string) {
  try {
    const response = await fetch(`${API_BASE}/odds/correlated?market_id=${marketId}`);
    const data = await response.json();
    
    return data.correlations || [];
  } catch (error) {
    return { error: 'Failed to fetch correlated odds' };
  }
}
```

##### Step 3: Create Snap Website Integration

**File:** `metamask-snap/website/index.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>NexHacks MetaMask Snap</title>
</head>
<body>
  <h1>NexHacks Polymarket Integration</h1>
  
  <button id="connect-snap">Connect Snap</button>
  <button id="get-trending">Get Trending Markets</button>
  <button id="get-parlays">Get Parlay Suggestions</button>
  
  <div id="results"></div>
  
  <script>
    const snapId = 'npm:nexhacks-metamask-snap';
    
    document.getElementById('connect-snap').onclick = async () => {
      try {
        await window.ethereum.request({
          method: 'wallet_requestSnaps',
          params: { [snapId]: {} }
        });
        alert('Snap connected!');
      } catch (error) {
        console.error(error);
      }
    };
    
    document.getElementById('get-trending').onclick = async () => {
      try {
        const result = await window.ethereum.request({
          method: 'wallet_invokeSnap',
          params: {
            snapId,
            request: { method: 'get_trending_markets' }
          }
        });
        document.getElementById('results').innerHTML = JSON.stringify(result, null, 2);
      } catch (error) {
        console.error(error);
      }
    };
    
    document.getElementById('get-parlays').onclick = async () => {
      const marketId = prompt('Enter market ID:');
      if (!marketId) return;
      
      try {
        const result = await window.ethereum.request({
          method: 'wallet_invokeSnap',
          params: {
            snapId,
            request: { 
              method: 'get_parlay_suggestions',
              params: { marketId }
            }
          }
        });
        document.getElementById('results').innerHTML = JSON.stringify(result, null, 2);
      } catch (error) {
        console.error(error);
      }
    };
  </script>
</body>
</html>
```

### 3. Zapier Integration

#### Purpose
Enable webhook-based parlay alerts and automation.

#### Implementation Steps

##### Step 1: Create Webhook Endpoints

**File:** `api/main.py` (add these endpoints)

```python
from fastapi import BackgroundTasks
import httpx

@app.post("/webhooks/parlay-alert")
async def create_parlay_alert(
    webhook_url: str = Query(..., description="Zapier webhook URL"),
    market_id: str = Query(None, description="Specific market to watch"),
    min_correlation: float = Query(0.7, description="Minimum correlation score"),
    background_tasks: BackgroundTasks
):
    """
    Register a webhook to receive parlay alerts
    """
    # Store webhook in database
    conn = SupabaseConnection()
    client = conn.get_client()
    
    webhook_record = {
        "webhook_url": webhook_url,
        "market_id": market_id,
        "min_correlation": min_correlation,
        "active": True
    }
    
    client.table("webhooks").insert(webhook_record).execute()
    
    return {"success": True, "message": "Webhook registered"}

@app.post("/webhooks/trigger")
async def trigger_webhook(
    webhook_id: str,
    data: dict
):
    """
    Internal endpoint to trigger webhooks
    """
    # Get webhook from database
    conn = SupabaseConnection()
    client = conn.get_client()
    
    webhook = client.table("webhooks").select("*").eq("id", webhook_id).execute()
    
    if not webhook.data:
        return {"error": "Webhook not found"}
    
    webhook_url = webhook.data[0]["webhook_url"]
    
    # Send POST request to webhook
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(webhook_url, json=data, timeout=10)
            return {"success": True, "status": response.status_code}
        except Exception as e:
            return {"error": str(e)}

# Background task to check for new parlay opportunities
async def check_parlay_opportunities():
    """Periodically check for new parlay opportunities and trigger webhooks"""
    conn = SupabaseConnection()
    client = conn.get_client()
    
    # Get active webhooks
    webhooks = client.table("webhooks").select("*").eq("active", True).execute()
    
    # Get trending markets
    trending = trending_service.get_trending_markets(limit=10)
    
    for market in trending:
        market_id = market["market_id"]
        
        # Get parlay suggestions
        suggestions = get_parlay_suggestions(market_id, "americanfootball_nfl")
        
        if suggestions.get("suggestions"):
            # Trigger webhooks
            for webhook in webhooks.data:
                if webhook["market_id"] is None or webhook["market_id"] == market_id:
                    correlation = suggestions["suggestions"][0].get("correlation_score", 0)
                    
                    if correlation >= webhook["min_correlation"]:
                        await trigger_webhook(webhook["id"], {
                            "market_id": market_id,
                            "market_question": market["question"],
                            "suggestions": suggestions["suggestions"]
                        })
```

##### Step 2: Create Webhook Table

**File:** `database/migrations/007_create_webhooks_table.sql`

```sql
-- Migration: Create Webhooks Table
-- Stores webhook configurations for Zapier and other integrations

CREATE TABLE IF NOT EXISTS webhooks (
    id BIGSERIAL PRIMARY KEY,
    webhook_url TEXT NOT NULL,
    market_id TEXT REFERENCES markets(market_id),
    min_correlation DECIMAL(5, 4) DEFAULT 0.7,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_triggered TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_webhooks_active ON webhooks(active);
CREATE INDEX IF NOT EXISTS idx_webhooks_market ON webhooks(market_id);
```

##### Step 3: Create Zapier Template

**File:** `zapier/template.json`

```json
{
  "name": "NexHacks Parlay Alerts",
  "description": "Get notified when new parlay opportunities are detected",
  "trigger": {
    "type": "webhook",
    "url": "https://your-api.com/api/webhooks/zapier",
    "method": "POST"
  },
  "actions": [
    {
      "type": "slack",
      "channel": "#parlay-alerts",
      "message": "New parlay opportunity: {{market_question}}\nExpected return: {{expected_return}}%"
    }
  ]
}
```

## Tier 2: Extended Integrations (Week 3-4)

### Binance API Integration

**File:** `services/binance_api.py`

```python
"""
Binance API Service
Fetches crypto prices and correlates with Polymarket markets
"""

import requests
from typing import Dict, List

class BinanceAPIService:
    BASE_URL = "https://api.binance.com/api/v3"
    
    def get_ticker_price(self, symbol: str) -> Dict:
        """Get current price for a symbol"""
        response = requests.get(f"{self.BASE_URL}/ticker/price", params={"symbol": symbol})
        return response.json()
    
    def get_24h_ticker(self, symbol: str) -> Dict:
        """Get 24h ticker statistics"""
        response = requests.get(f"{self.BASE_URL}/ticker/24hr", params={"symbol": symbol})
        return response.json()
    
    def find_crypto_correlations(self, market_question: str) -> List[Dict]:
        """Find crypto markets correlated with Polymarket question"""
        # Extract crypto symbols from question
        cryptos = ["BTC", "ETH", "SOL", "DOGE", "ADA"]
        found = []
        
        for crypto in cryptos:
            if crypto in market_question.upper():
                ticker = self.get_24h_ticker(f"{crypto}USDT")
                found.append({
                    "symbol": crypto,
                    "price": float(ticker.get("lastPrice", 0)),
                    "change_24h": float(ticker.get("priceChangePercent", 0))
                })
        
        return found
```

## Testing

### Test Script

**File:** `scripts/test_integrations.py`

```python
"""Test third-party integrations"""

from services.odds_api import OddsAPIService
from services.correlation_engine import CorrelationEngine

def test_odds_api():
    """Test The Odds API connection"""
    service = OddsAPIService()
    sports = service.get_sports()
    print(f"Available sports: {len(sports)}")
    
    odds = service.get_odds("americanfootball_nfl")
    print(f"NFL games: {len(odds)}")

def test_correlation():
    """Test correlation engine"""
    engine = CorrelationEngine()
    correlations = engine.find_correlated_markets(
        "Will the Chiefs win the Super Bowl?",
        "americanfootball_nfl"
    )
    print(f"Found {len(correlations)} correlations")

if __name__ == "__main__":
    test_odds_api()
    test_correlation()
```

## Environment Variables

Add to `.env`:

```bash
# The Odds API
THE_ODDS_API_KEY=your_api_key_here

# Binance (optional)
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here

# Webhook base URL
WEBHOOK_BASE_URL=https://your-api.com/api
```

## Deployment Checklist

- [ ] Get API keys for all services
- [ ] Set environment variables
- [ ] Run database migrations
- [ ] Deploy API endpoints
- [ ] Test each integration
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Set up error logging
