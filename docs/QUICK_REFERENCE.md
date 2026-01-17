# MongoDB Quick Reference

Quick reference guide for common MongoDB operations in the NexHacks project.

## Connection

```python
from database.mongodb_connection import MongoDBConnection

conn = MongoDBConnection()
db = conn.connect()
# ... operations ...
conn.close()
```

## Collections

```python
markets = db["markets"]
user_trades = db["user_trades"]
correlations = db["trade_correlations"]
related_trades = db["related_trades"]
parlay_suggestions = db["parlay_suggestions"]
hedge_opportunities = db["hedge_opportunities"]
```

## Common Operations

### Insert

```python
# Single
markets.insert_one({"market_id": "0x123", "question": "..."})

# Multiple
markets.insert_many([{...}, {...}])
```

### Find

```python
# One document
market = markets.find_one({"market_id": "0x123"})

# Multiple documents
results = markets.find({"tag_label": "finance"})

# With limit
results = markets.find({}).limit(10)

# Sort
results = markets.find({}).sort("created_at", -1)  # -1 = descending
```

### Update

```python
# Update one
markets.update_one(
    {"market_id": "0x123"},
    {"$set": {"active": False}}
)

# Update many
markets.update_many(
    {"tag_label": "finance"},
    {"$set": {"updated_at": datetime.utcnow()}}
)

# Upsert (insert if not exists)
markets.update_one(
    {"market_id": "0x123"},
    {"$set": {...}},
    upsert=True
)
```

### Delete

```python
# Delete one
markets.delete_one({"market_id": "0x123"})

# Delete many
markets.delete_many({"active": False})
```

## Query Operators

```python
# Comparison
{"price": {"$gt": 0.5}}          # Greater than
{"price": {"$gte": 0.5}}         # Greater than or equal
{"price": {"$lt": 1.0}}          # Less than
{"price": {"$lte": 1.0}}         # Less than or equal
{"price": {"$ne": 0.5}}          # Not equal
{"price": {"$in": [0.5, 0.6]}}   # In array
{"price": {"$nin": [0.5, 0.6]}}  # Not in array

# Logical
{"$or": [{"tag": "finance"}, {"tag": "tech"}]}
{"$and": [{"active": True}, {"closed": False}]}
{"$not": {"active": False}}

# Text search
{"$text": {"$search": "Bitcoin"}}

# Exists
{"question": {"$exists": True}}
```

## Update Operators

```python
{"$set": {"field": "value"}}           # Set field
{"$unset": {"field": ""}}              # Remove field
{"$inc": {"count": 1}}                  # Increment
{"$push": {"array": "value"}}           # Add to array
{"$pull": {"array": "value"}}           # Remove from array
{"$addToSet": {"array": "value"}}      # Add if not exists
```

## Common Queries

### Get Active Markets

```python
active = markets.find({"active": True})
```

### Get Markets by Category

```python
finance = markets.find({"tag_label": "finance"})
```

### Search Markets by Text

```python
results = markets.find(
    {"$text": {"$search": "Bitcoin"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])
```

### Get User Trades

```python
trades = user_trades.find({"user_id": "user_123"})
```

### Find Correlations

```python
corr = correlations.find({
    "$or": [
        {"market_id_1": "0x123"},
        {"market_id_2": "0x123"}
    ],
    "correlation_score": {"$gte": 0.7}
})
```

### Count Documents

```python
count = markets.count_documents({"active": True})
```

## Projection (Select Fields)

```python
# Include only specific fields
markets.find({}, {"market_id": 1, "question": 1})

# Exclude fields
markets.find({}, {"_id": 0, "clob_token_ids": 0})
```

## Sorting

```python
# Ascending
.find({}).sort("created_at", 1)

# Descending
.find({}).sort("created_at", -1)

# Multiple fields
.find({}).sort([("tag_label", 1), ("created_at", -1)])
```

## Aggregation Examples

### Group by Category

```python
pipeline = [
    {"$group": {
        "_id": "$tag_label",
        "count": {"$sum": 1}
    }}
]
results = markets.aggregate(pipeline)
```

### Average Price

```python
pipeline = [
    {"$match": {"user_id": "user_123"}},
    {"$group": {
        "_id": None,
        "avg_price": {"$avg": "$price"}
    }}
]
```

## Indexes

```python
# Create index
markets.create_index("market_id", unique=True)

# Create text index
markets.create_index([("question", "text"), ("tag_label", "text")])

# Create compound index
markets.create_index([("tag_label", 1), ("active", 1)])
```

## Error Handling

```python
from pymongo.errors import DuplicateKeyError

try:
    markets.insert_one({...})
except DuplicateKeyError:
    print("Duplicate market_id")
```

## Date Operations

```python
from datetime import datetime, timedelta

# Current time
now = datetime.utcnow()

# Yesterday
yesterday = datetime.utcnow() - timedelta(days=1)

# Query by date range
markets.find({
    "created_at": {
        "$gte": yesterday,
        "$lte": now
    }
})
```

## Useful Methods

```python
# Check if document exists
exists = markets.find_one({"market_id": "0x123"}) is not None

# Get distinct values
categories = markets.distinct("tag_label")

# Drop collection (careful!)
# markets.drop()

# Get collection stats
stats = db.command("collStats", "markets")
```

## Connection String Formats

### Atlas
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### Local
```
mongodb://localhost:27017/
```

## Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "nexhacks_polymarket")
```

## Common Patterns

### Upsert Pattern

```python
markets.update_one(
    {"market_id": market_id},
    {"$set": market_data},
    upsert=True
)
```

### Find or Create

```python
market = markets.find_one({"market_id": market_id})
if not market:
    markets.insert_one(market_data)
```

### Batch Insert with Error Handling

```python
try:
    markets.insert_many(documents, ordered=False)
except BulkWriteError as e:
    # Some documents may have been inserted
    print(f"Inserted: {e.details['nInserted']}")
```

## Performance Tips

1. Always use `.limit()` for large result sets
2. Use projection to return only needed fields
3. Query on indexed fields
4. Use `bulk_write()` for multiple operations
5. Use aggregation for complex queries

## Collection Names Reference

| Collection | Purpose |
|------------|---------|
| `markets` | Polymarket market data |
| `user_trades` | User trading history |
| `trade_correlations` | Market correlations |
| `related_trades` | Related/pairs trades |
| `parlay_suggestions` | Parlay recommendations |
| `hedge_opportunities` | Hedge suggestions |

## Field Types Reference

| Field | Type | Example |
|-------|------|---------|
| `market_id` | String | `"0x1234567890abcdef"` |
| `question` | String | `"Will Bitcoin reach $100k?"` |
| `tag_label` | String | `"finance"` |
| `active` | Boolean | `true` |
| `correlation_score` | Number | `0.85` |
| `timestamp` | Date | `ISODate("2024-01-15T10:30:00Z")` |
| `shares` | Number | `100` |
| `price` | Number | `0.65` |

---

## Quick Commands

```bash
# Test connection
python database/test_connection.py

# Initialize database
python database/init_db.py

# Check MongoDB version (local)
mongod --version
```

---

For more details, see:
- [MONGODB_SETUP.md](./MONGODB_SETUP.md) - Setup instructions
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - Schema documentation
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Code examples
