# MongoDB Implementation Guide

Complete implementation guide with code examples for the NexHacks Polymarket Correlation Tool.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Connection Setup](#connection-setup)
3. [Basic CRUD Operations](#basic-crud-operations)
4. [Market Data Operations](#market-data-operations)
5. [User Trade Operations](#user-trade-operations)
6. [Correlation Operations](#correlation-operations)
7. [Query Examples](#query-examples)
8. [Advanced Patterns](#advanced-patterns)

---

## Project Structure

```
NexHacks/
├── database/
│   ├── __init__.py
│   ├── mongodb_connection.py      # Connection handler
│   ├── schema.py                  # Collection creation & indexes
│   ├── init_db.py                 # Database initialization
│   └── test_connection.py         # Connection testing
├── docs/
│   ├── MONGODB_SETUP.md
│   ├── DATABASE_SCHEMA.md
│   ├── IMPLEMENTATION_GUIDE.md
│   └── QUICK_REFERENCE.md
├── .env                           # Environment variables
└── requirements.txt
```

---

## Connection Setup

### Basic Connection

```python
from database.mongodb_connection import MongoDBConnection

# Initialize connection
conn = MongoDBConnection()
db = conn.connect(database_name="nexhacks_polymarket")

# Get collections
markets = db["markets"]
user_trades = db["user_trades"]

# Close connection when done
conn.close()
```

### Connection Context Manager (Recommended)

```python
from database.mongodb_connection import MongoDBConnection

def get_database():
    """Get database instance"""
    conn = MongoDBConnection()
    db = conn.connect()
    return db, conn

# Usage
db, conn = get_database()
try:
    # Your operations here
    markets = db["markets"]
    result = markets.find_one({"market_id": "0x123"})
finally:
    conn.close()
```

---

## Basic CRUD Operations

### Create (Insert)

```python
# Insert single document
market = {
    "market_id": "0x1234567890abcdef",
    "question": "Will Bitcoin reach $100k?",
    "tag_label": "finance",
    "active": True
}
result = markets.insert_one(market)
print(f"Inserted ID: {result.inserted_id}")

# Insert multiple documents
markets_list = [
    {"market_id": "0x111", "question": "Market 1", "tag_label": "finance"},
    {"market_id": "0x222", "question": "Market 2", "tag_label": "politics"}
]
result = markets.insert_many(markets_list)
print(f"Inserted {len(result.inserted_ids)} documents")
```

### Read (Query)

```python
# Find one document
market = markets.find_one({"market_id": "0x1234567890abcdef"})

# Find multiple documents
all_markets = markets.find({"tag_label": "finance"})
for market in all_markets:
    print(market["question"])

# Find with conditions
active_markets = markets.find({
    "active": True,
    "tag_label": {"$in": ["finance", "tech"]}
})

# Count documents
count = markets.count_documents({"active": True})
```

### Update

```python
# Update one document
result = markets.update_one(
    {"market_id": "0x1234567890abcdef"},
    {"$set": {"active": False, "updated_at": datetime.utcnow()}}
)
print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

# Update multiple documents
result = markets.update_many(
    {"tag_label": "finance"},
    {"$set": {"updated_at": datetime.utcnow()}}
)

# Upsert (insert if doesn't exist, update if exists)
markets.update_one(
    {"market_id": "0x1234567890abcdef"},
    {"$set": {"question": "Updated question"}},
    upsert=True
)
```

### Delete

```python
# Delete one document
result = markets.delete_one({"market_id": "0x1234567890abcdef"})

# Delete multiple documents
result = markets.delete_many({"active": False})

# Delete all (use with caution!)
# markets.delete_many({})
```

---

## Market Data Operations

### Import Markets from CSV

```python
import pandas as pd
from datetime import datetime
from database.mongodb_connection import MongoDBConnection

def import_markets_from_csv(csv_path, db):
    """Import markets from CSV file"""
    df = pd.read_csv(csv_path)
    markets = db["markets"]
    
    documents = []
    for _, row in df.iterrows():
        doc = {
            "market_id": row["market_id"],
            "market_slug": row.get("market_slug", ""),
            "question": row.get("question", ""),
            "tag_label": row.get("tag_label", ""),
            "tag_id": row.get("tag_id", 0),
            "clob_token_ids": row.get("clob_token_ids", ""),
            "active": True,
            "closed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        documents.append(doc)
    
    # Insert in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        markets.insert_many(batch, ordered=False)  # Continue on duplicate errors
    
    print(f"Imported {len(documents)} markets")

# Usage
conn = MongoDBConnection()
db = conn.connect()
import_markets_from_csv("polymarket_events_by_tags.csv", db)
conn.close()
```

### Search Markets by Text

```python
def search_markets_by_text(db, search_term, limit=10):
    """Search markets using text index"""
    markets = db["markets"]
    
    results = markets.find(
        {"$text": {"$search": search_term}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(limit)
    
    return list(results)

# Usage
results = search_markets_by_text(db, "Bitcoin price", limit=5)
for market in results:
    print(f"{market['question']} (score: {market.get('score', 0)})")
```

### Get Markets by Category

```python
def get_markets_by_category(db, category, active_only=True):
    """Get all markets in a category"""
    markets = db["markets"]
    
    query = {"tag_label": category}
    if active_only:
        query["active"] = True
    
    return list(markets.find(query))

# Usage
finance_markets = get_markets_by_category(db, "finance")
```

---

## User Trade Operations

### Record a User Trade

```python
from datetime import datetime
from bson import ObjectId

def record_user_trade(db, user_id, market_id, trade_type, shares, price):
    """Record a user's trade"""
    user_trades = db["user_trades"]
    
    trade = {
        "user_id": user_id,
        "market_id": market_id,
        "trade_type": trade_type,  # "yes" or "no"
        "shares": shares,
        "price": price,
        "total_cost": shares * price,
        "timestamp": datetime.utcnow(),
        "status": "open",
        "notes": ""
    }
    
    result = user_trades.insert_one(trade)
    return result.inserted_id

# Usage
trade_id = record_user_trade(
    db, 
    user_id="user_12345",
    market_id="0x1234567890abcdef",
    trade_type="yes",
    shares=100,
    price=0.65
)
```

### Get User's Trading History

```python
def get_user_trades(db, user_id, limit=50):
    """Get user's trading history"""
    user_trades = db["user_trades"]
    
    return list(user_trades.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit))

# Usage
trades = get_user_trades(db, "user_12345")
for trade in trades:
    print(f"{trade['market_id']}: {trade['trade_type']} {trade['shares']} shares")
```

### Get User's Open Positions

```python
def get_user_open_positions(db, user_id):
    """Get user's currently open positions"""
    user_trades = db["user_trades"]
    
    return list(user_trades.find({
        "user_id": user_id,
        "status": "open"
    }))
```

---

## Correlation Operations

### Store Correlation

```python
def store_correlation(db, market_id_1, market_id_2, correlation_score, 
                     correlation_type, similarity_score=0, price_correlation=0):
    """Store a correlation between two markets"""
    correlations = db["trade_correlations"]
    
    # Ensure market_id_1 < market_id_2 for consistency
    if market_id_1 > market_id_2:
        market_id_1, market_id_2 = market_id_2, market_id_1
    
    correlation = {
        "market_id_1": market_id_1,
        "market_id_2": market_id_2,
        "correlation_score": correlation_score,
        "correlation_type": correlation_type,  # "related", "correlated", "inverse"
        "calculation_method": "text_similarity + price_correlation",
        "similarity_score": similarity_score,
        "price_correlation": price_correlation,
        "category_match": False,
        "calculated_at": datetime.utcnow(),
        "confidence": abs(correlation_score)
    }
    
    # Upsert to update if exists
    correlations.update_one(
        {"market_id_1": market_id_1, "market_id_2": market_id_2},
        {"$set": correlation},
        upsert=True
    )

# Usage
store_correlation(
    db,
    market_id_1="0x111",
    market_id_2="0x222",
    correlation_score=0.85,
    correlation_type="correlated",
    similarity_score=0.92,
    price_correlation=0.78
)
```

### Find Correlated Markets

```python
def find_correlated_markets(db, market_id, correlation_type="correlated", 
                            min_score=0.7, limit=10):
    """Find markets correlated with a given market"""
    correlations = db["trade_correlations"]
    
    # Search in both directions (market_id_1 or market_id_2)
    results = correlations.find({
        "$or": [
            {"market_id_1": market_id},
            {"market_id_2": market_id}
        ],
        "correlation_type": correlation_type,
        "correlation_score": {"$gte": min_score}
    }).sort("correlation_score", -1).limit(limit)
    
    # Extract the other market ID
    correlated = []
    for corr in results:
        other_market = corr["market_id_2"] if corr["market_id_1"] == market_id else corr["market_id_1"]
        correlated.append({
            "market_id": other_market,
            "correlation_score": corr["correlation_score"],
            "similarity_score": corr.get("similarity_score", 0),
            "price_correlation": corr.get("price_correlation", 0)
        })
    
    return correlated

# Usage
correlated = find_correlated_markets(db, "0x1234567890abcdef", min_score=0.75)
```

### Find Inverse Correlations (Hedge Opportunities)

```python
def find_hedge_opportunities(db, market_id, min_inverse_correlation=-0.5):
    """Find markets with inverse correlation (for hedging)"""
    correlations = db["trade_correlations"]
    
    results = correlations.find({
        "$or": [
            {"market_id_1": market_id},
            {"market_id_2": market_id}
        ],
        "correlation_score": {"$lte": min_inverse_correlation}
    }).sort("correlation_score", 1)  # Most negative first
    
    hedges = []
    for corr in results:
        other_market = corr["market_id_2"] if corr["market_id_1"] == market_id else corr["market_id_1"]
        hedges.append({
            "market_id": other_market,
            "inverse_correlation": corr["correlation_score"],
            "confidence": abs(corr["correlation_score"])
        })
    
    return hedges
```

---

## Query Examples

### Get Related Trades for Frontend Table

```python
def get_related_trades_table(db, market_id):
    """Get data for 'Related Trades' table"""
    # Get related trades
    related = db["related_trades"].find({"market_id": market_id})
    
    # Get market details
    markets = db["markets"]
    results = []
    
    for rel in related:
        market = markets.find_one({"market_id": rel["related_market_id"]})
        if market:
            results.append({
                "market_id": market["market_id"],
                "question": market["question"],
                "relationship_type": rel["relationship_type"],
                "relationship_strength": rel["relationship_strength"]
            })
    
    return results
```

### Get Correlated Trades with Metrics

```python
def get_correlated_trades_table(db, market_id):
    """Get data for 'Correlated Trades' table with metrics"""
    correlations = db["trade_correlations"]
    markets = db["markets"]
    
    # Find correlations
    corr_results = correlations.find({
        "$or": [
            {"market_id_1": market_id},
            {"market_id_2": market_id}
        ],
        "correlation_type": "correlated",
        "correlation_score": {"$gte": 0.6}
    }).sort("correlation_score", -1)
    
    results = []
    for corr in corr_results:
        other_id = corr["market_id_2"] if corr["market_id_1"] == market_id else corr["market_id_1"]
        market = markets.find_one({"market_id": other_id})
        
        if market:
            results.append({
                "market_id": market["market_id"],
                "question": market["question"],
                "correlation_score": corr["correlation_score"],
                "similarity_score": corr.get("similarity_score", 0),
                "price_correlation": corr.get("price_correlation", 0),
                "calculated_at": corr["calculated_at"]
            })
    
    return results
```

### Generate Parlay Suggestions

```python
def generate_parlay_suggestions(db, user_id, base_market_id):
    """Generate parlay suggestions based on user's trade"""
    # Find correlated markets
    correlated = find_correlated_markets(db, base_market_id, min_score=0.7, limit=5)
    
    # Get market details
    markets = db["markets"]
    base_market = markets.find_one({"market_id": base_market_id})
    
    if not base_market:
        return []
    
    suggested_markets = []
    for corr in correlated:
        market = markets.find_one({"market_id": corr["market_id"]})
        if market and market.get("active"):
            suggested_markets.append({
                "market_id": market["market_id"],
                "reason": f"High correlation ({corr['correlation_score']:.2f}) with {base_market['question']}",
                "correlation_score": corr["correlation_score"],
                "expected_contribution": 1.0 + corr["correlation_score"] * 0.3
            })
    
    # Calculate expected return (simplified)
    expected_return = 1.0
    for sm in suggested_markets:
        expected_return *= sm["expected_contribution"]
    
    # Store suggestion
    parlay_suggestions = db["parlay_suggestions"]
    suggestion = {
        "user_id": user_id,
        "base_market_id": base_market_id,
        "suggested_markets": suggested_markets,
        "expected_return": expected_return,
        "risk_level": "medium" if len(suggested_markets) <= 3 else "high",
        "confidence": sum(sm["correlation_score"] for sm in suggested_markets) / len(suggested_markets) if suggested_markets else 0,
        "created_at": datetime.utcnow(),
        "viewed": False,
        "accepted": False
    }
    
    parlay_suggestions.insert_one(suggestion)
    return suggestion
```

---

## Advanced Patterns

### Batch Operations

```python
from pymongo import UpdateOne

def batch_update_correlations(db, correlations_list):
    """Batch update correlations efficiently"""
    correlations = db["trade_correlations"]
    
    operations = []
    for corr in correlations_list:
        # Ensure consistent ordering
        m1, m2 = sorted([corr["market_id_1"], corr["market_id_2"]])
        
        operations.append(
            UpdateOne(
                {"market_id_1": m1, "market_id_2": m2},
                {"$set": corr},
                upsert=True
            )
        )
    
    result = correlations.bulk_write(operations)
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_count}")
```

### Aggregation Pipeline

```python
def get_user_portfolio_summary(db, user_id):
    """Get user's portfolio summary using aggregation"""
    user_trades = db["user_trades"]
    
    pipeline = [
        {"$match": {"user_id": user_id, "status": "open"}},
        {"$group": {
            "_id": "$trade_type",
            "total_shares": {"$sum": "$shares"},
            "total_cost": {"$sum": "$total_cost"},
            "avg_price": {"$avg": "$price"},
            "count": {"$sum": 1}
        }}
    ]
    
    results = list(user_trades.aggregate(pipeline))
    return results
```

### Text Search with Filters

```python
def search_markets_advanced(db, search_term, category=None, active_only=True):
    """Advanced market search with filters"""
    markets = db["markets"]
    
    query = {"$text": {"$search": search_term}}
    
    if category:
        query["tag_label"] = category
    
    if active_only:
        query["active"] = True
    
    return list(markets.find(
        query,
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(20))
```

---

## Error Handling

```python
from pymongo.errors import DuplicateKeyError, ConnectionFailure

def safe_insert_market(db, market_data):
    """Safely insert market with error handling"""
    markets = db["markets"]
    
    try:
        result = markets.insert_one(market_data)
        return {"success": True, "id": result.inserted_id}
    except DuplicateKeyError:
        # Market already exists, update instead
        markets.update_one(
            {"market_id": market_data["market_id"]},
            {"$set": market_data}
        )
        return {"success": True, "updated": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Performance Tips

1. **Use indexes** - Always query on indexed fields
2. **Limit results** - Use `.limit()` to avoid loading too much data
3. **Project fields** - Use `{"field": 1}` to return only needed fields
4. **Batch operations** - Use `bulk_write()` for multiple updates
5. **Connection pooling** - Reuse connections, don't create new ones for each operation

---

## Next Steps

- See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for common operations
- Review [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for data structure
- Start building your correlation algorithms!
