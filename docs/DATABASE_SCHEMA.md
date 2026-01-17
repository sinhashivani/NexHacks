# Database Schema Documentation

Complete schema documentation for the NexHacks Polymarket Correlation Tool database.

## Database Overview

**Database Name**: `nexhacks_polymarket`

**Collections**: 6
- `markets` - Polymarket market data
- `user_trades` - User trading history
- `trade_correlations` - Calculated correlations between markets
- `related_trades` - Related/pairs trading opportunities
- `parlay_suggestions` - Suggested parlay combinations
- `hedge_opportunities` - Hedge suggestions for user trades

---

## Collection: `markets`

Stores all Polymarket market data fetched from the API.

### Schema

```javascript
{
  "_id": ObjectId,                    // Auto-generated MongoDB ID
  "market_id": String,                // Unique Polymarket market ID (indexed, unique)
  "market_slug": String,              // Market URL slug
  "question": String,                 // Market question/title (indexed for text search)
  "tag_label": String,                // Category tag (e.g., "finance", "politics") (indexed)
  "tag_id": Number,                   // Tag ID from Polymarket
  "clob_token_ids": String,           // JSON string of token IDs
  "active": Boolean,                  // Is market active? (indexed)
  "closed": Boolean,                  // Is market closed?
  "created_at": Date,                 // When document was created
  "updated_at": Date                  // Last update timestamp
}
```

### Indexes

- `market_id` (unique) - Fast lookup by market ID
- `question` + `tag_label` (text) - Full-text search on questions
- `tag_label` - Filter by category
- `active` - Filter active markets

### Example Document

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "market_id": "0x1234567890abcdef",
  "market_slug": "will-bitcoin-reach-100k-by-2024",
  "question": "Will Bitcoin reach $100,000 by December 2024?",
  "tag_label": "finance",
  "tag_id": 42,
  "clob_token_ids": "[123, 456]",
  "active": true,
  "closed": false,
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z")
}
```

### Use Cases

- Store all Polymarket markets for correlation analysis
- Text search for similar questions
- Filter by category/tag
- Track active vs closed markets

---

## Collection: `user_trades`

Stores user's trading history and positions.

### Schema

```javascript
{
  "_id": ObjectId,                    // Auto-generated MongoDB ID
  "user_id": String,                  // User identifier (indexed)
  "market_id": String,                 // Market ID from markets collection (indexed)
  "trade_type": String,               // "yes" or "no" (buying yes or no shares)
  "shares": Number,                   // Number of shares
  "price": Number,                    // Price per share at time of trade
  "total_cost": Number,               // Total cost of trade
  "timestamp": Date,                  // When trade was placed (indexed)
  "status": String,                   // "open", "closed", "cancelled"
  "notes": String                     // Optional user notes
}
```

### Indexes

- `user_id` + `market_id` - Fast lookup of user's trades for a market
- `market_id` - Find all users who traded this market
- `timestamp` - Sort by time, find recent trades

### Example Document

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "user_id": "user_12345",
  "market_id": "0x1234567890abcdef",
  "trade_type": "yes",
  "shares": 100,
  "price": 0.65,
  "total_cost": 65.0,
  "timestamp": ISODate("2024-01-15T14:22:00Z"),
  "status": "open",
  "notes": "Bullish on Bitcoin"
}
```

### Use Cases

- Track user's trading history
- Identify which markets user has traded
- Calculate user's portfolio
- Generate personalized recommendations

---

## Collection: `trade_correlations`

Stores calculated correlations between markets.

### Schema

```javascript
{
  "_id": ObjectId,                    // Auto-generated MongoDB ID
  "market_id_1": String,              // First market ID (indexed)
  "market_id_2": String,              // Second market ID (indexed)
  "correlation_score": Number,        // Correlation value (-1 to 1) (indexed)
  "correlation_type": String,         // "related", "correlated", "inverse" (indexed)
  "calculation_method": String,       // How correlation was calculated
  "similarity_score": Number,         // Text similarity score (0 to 1)
  "price_correlation": Number,        // Price movement correlation (-1 to 1)
  "category_match": Boolean,          // Same category/tag?
  "calculated_at": Date,              // When correlation was calculated
  "confidence": Number                // Confidence in correlation (0 to 1)
}
```

### Indexes

- `market_id_1` + `market_id_2` (unique) - Fast lookup of correlation between two markets
- `correlation_score` - Sort by correlation strength
- `correlation_type` - Filter by type (related/correlated/inverse)

### Example Document

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "market_id_1": "0x1234567890abcdef",
  "market_id_2": "0xabcdef1234567890",
  "correlation_score": 0.85,
  "correlation_type": "correlated",
  "calculation_method": "text_similarity + price_correlation",
  "similarity_score": 0.92,
  "price_correlation": 0.78,
  "category_match": true,
  "calculated_at": ISODate("2024-01-15T15:00:00Z"),
  "confidence": 0.88
}
```

### Use Cases

- Find correlated markets for parlay suggestions
- Identify inverse correlations for hedging
- Power the "Related Trades" and "Correlated Trades" tables
- Calculate relationship strength between markets

---

## Collection: `related_trades`

Stores pairs trading and related trade opportunities.

### Schema

```javascript
{
  "_id": ObjectId,                    // Auto-generated MongoDB ID
  "market_id": String,                 // Original market ID (indexed)
  "related_market_id": String,        // Related market ID (indexed)
  "relationship_type": String,        // "company_pair", "sector", "event", "geographic" (indexed)
  "relationship_strength": Number,     // How strong the relationship (0 to 1)
  "description": String,              // Human-readable description
  "examples": [String],               // Example pairs
  "created_at": Date,
  "updated_at": Date
}
```

### Indexes

- `market_id` - Find all related trades for a market
- `related_market_id` - Reverse lookup
- `relationship_type` - Filter by relationship type

### Example Document

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "market_id": "0x1234567890abcdef",
  "related_market_id": "0x9876543210fedcba",
  "relationship_type": "company_pair",
  "relationship_strength": 0.95,
  "description": "Apple and Microsoft stock performance are historically correlated",
  "examples": ["AAPL vs MSFT earnings", "Tech sector movements"],
  "created_at": ISODate("2024-01-15T16:00:00Z"),
  "updated_at": ISODate("2024-01-15T16:00:00Z")
}
```

### Use Cases

- Power "Related Trades" table
- Pairs trading suggestions
- Company/sector relationships
- Event-based correlations

---

## Collection: `parlay_suggestions`

Stores suggested parlay combinations for users.

### Schema

```javascript
{
  "_id": ObjectId,                    // Auto-generated MongoDB ID
  "user_id": String,                  // User identifier (indexed)
  "base_market_id": String,           // Market user already traded (indexed)
  "suggested_markets": [              // Array of suggested markets to add
    {
      "market_id": String,
      "reason": String,               // Why this market was suggested
      "correlation_score": Number,
      "expected_contribution": Number  // How much this adds to parlay
    }
  ],
  "expected_return": Number,           // Expected return multiplier (indexed)
  "risk_level": String,               // "low", "medium", "high"
  "confidence": Number,                // Confidence in suggestion (0 to 1)
  "created_at": Date,
  "viewed": Boolean,                   // Has user viewed this?
  "accepted": Boolean                  // Did user accept suggestion?
}
```

### Indexes

- `user_id` - Find all suggestions for a user
- `base_market_id` - Find suggestions based on a market
- `expected_return` - Sort by potential returns

### Example Document

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439015"),
  "user_id": "user_12345",
  "base_market_id": "0x1234567890abcdef",
  "suggested_markets": [
    {
      "market_id": "0xabcdef1234567890",
      "reason": "High correlation (0.85) with your Bitcoin trade",
      "correlation_score": 0.85,
      "expected_contribution": 1.2
    },
    {
      "market_id": "0x1111111111111111",
      "reason": "Related tech sector market",
      "correlation_score": 0.72,
      "expected_contribution": 1.15
    }
  ],
  "expected_return": 2.5,
  "risk_level": "medium",
  "confidence": 0.82,
  "created_at": ISODate("2024-01-15T17:00:00Z"),
  "viewed": false,
  "accepted": false
}
```

### Use Cases

- Generate parlay suggestions for users
- Amplify returns through correlated trades
- Personalize recommendations based on user's existing trades

---

## Collection: `hedge_opportunities`

Stores hedge suggestions for user trades.

### Schema

```javascript
{
  "_id": ObjectId,                    // Auto-generated MongoDB ID
  "user_id": String,                  // User identifier (indexed)
  "original_trade_id": ObjectId,      // Reference to user_trades._id (indexed)
  "original_market_id": String,       // Market user traded
  "hedge_market_id": String,          // Suggested hedge market
  "hedge_type": String,               // "inverse", "opposite_outcome", "uncorrelated"
  "inverse_correlation": Number,      // Inverse correlation score (-1 to 1)
  "hedge_ratio": Number,              // Recommended hedge ratio (e.g., 0.5 = hedge 50%)
  "risk_reduction": Number,           // Expected risk reduction (0 to 1)
  "cost_impact": Number,              // Additional cost of hedge
  "description": String,              // Why this is a good hedge
  "created_at": Date,
  "viewed": Boolean,
  "accepted": Boolean
}
```

### Indexes

- `user_id` + `original_trade_id` - Find hedges for a specific trade
- `original_trade_id` - Find all hedge suggestions for a trade

### Example Document

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439016"),
  "user_id": "user_12345",
  "original_trade_id": ObjectId("507f1f77bcf86cd799439012"),
  "original_market_id": "0x1234567890abcdef",
  "hedge_market_id": "0x9999999999999999",
  "hedge_type": "inverse",
  "inverse_correlation": -0.78,
  "hedge_ratio": 0.5,
  "risk_reduction": 0.65,
  "cost_impact": 32.5,
  "description": "This market has strong inverse correlation (-0.78) with your Bitcoin trade. Hedging 50% reduces risk by 65%.",
  "created_at": ISODate("2024-01-15T18:00:00Z"),
  "viewed": false,
  "accepted": false
}
```

### Use Cases

- Suggest hedges for user's open positions
- Prevent users from selecting contradictory trades (e.g., team over + under)
- Risk management recommendations
- Identify inverse correlations

---

## Relationships Between Collections

```
markets (1) ──< (many) user_trades
markets (1) ──< (many) trade_correlations (market_id_1)
markets (1) ──< (many) trade_correlations (market_id_2)
markets (1) ──< (many) related_trades
markets (1) ──< (many) parlay_suggestions
markets (1) ──< (many) hedge_opportunities

user_trades (1) ──< (many) parlay_suggestions
user_trades (1) ──< (many) hedge_opportunities
```

---

## Data Flow

1. **Import Markets**: CSV → `markets` collection
2. **User Trades**: User action → `user_trades` collection
3. **Calculate Correlations**: `markets` → Algorithm → `trade_correlations`
4. **Find Related**: `markets` + `trade_correlations` → `related_trades`
5. **Generate Suggestions**: `user_trades` + `trade_correlations` → `parlay_suggestions` + `hedge_opportunities`

---

## Index Strategy

### Why These Indexes?

1. **Unique indexes** prevent duplicate data
2. **Text indexes** enable fast full-text search
3. **Compound indexes** optimize common query patterns
4. **Sorted indexes** enable efficient sorting and range queries

### Query Performance

- **Fast**: Queries using indexed fields
- **Medium**: Queries with partial index match
- **Slow**: Queries without indexes (full collection scan)

Always use indexed fields in your queries when possible!

---

## Best Practices

1. **Always use `market_id`** for lookups (it's unique and indexed)
2. **Store timestamps** for all documents (`created_at`, `updated_at`)
3. **Use ObjectId references** for relationships between collections
4. **Index frequently queried fields**
5. **Keep documents normalized** but denormalize for performance when needed
6. **Use arrays sparingly** - prefer separate documents for scalability

---

## Next Steps

- See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for code examples
- See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for common operations
