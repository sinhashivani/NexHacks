# Related Traded Markets Implementation Strategy

## Overview

The `get_related_traded` functionality finds markets related through **trading patterns** rather than just text similarity. This complements the existing similarity system which uses cosine similarity on text.

## Key Differences

| Feature | Similarity System | Related Traded System |
|---------|------------------|----------------------|
| **Method** | Text-based (TF-IDF + cosine similarity) | Pattern-based (events, sectors, entities) |
| **Data Source** | `similarity_scores` table | `related_trades` table + on-the-fly analysis |
| **Use Case** | "Markets with similar questions" | "Markets that trade together" |
| **Endpoint** | `/similar?event_title=...` | `/markets/{id}/related` or `/related?market_id=...` |

## Implementation Architecture

### 1. Relationship Types

The system identifies four types of relationships:

#### A. Event Relationships (`event`)
- **Definition**: Markets that belong to the same event
- **Strength**: 1.0 (100% - same event)
- **Detection**: Match `event_title` field
- **Example**: All markets for "MicroStrategy sells Bitcoin by ___ ?"

#### B. Sector Relationships (`sector`)
- **Definition**: Markets in the same category/tag
- **Strength**: 0.7-0.9 (depending on event overlap)
- **Detection**: Match `tag_label` field
- **Example**: All "Politics" markets, all "Crypto" markets

#### C. Company/Entity Pairs (`company_pair`)
- **Definition**: Markets mentioning the same companies/entities
- **Strength**: 0.6-0.9 (based on entity overlap)
- **Detection**: Extract entities from `question` field using heuristics
- **Example**: Markets about "Apple" and "Microsoft" stock

#### D. Geographic Relationships (`geographic`)
- **Definition**: Markets about the same location
- **Strength**: 0.5-0.8
- **Detection**: Extract location names from `question` field
- **Future**: Can be enhanced with NLP/NER

### 2. Data Flow

```
User Query (market_id/event_title)
    ↓
get_related_traded()
    ↓
┌─────────────────────────────────────┐
│ Strategy 1: Same event_title        │ → event relationship
│ Strategy 2: Same tag_label          │ → sector relationship
│ Strategy 3: Entity extraction       │ → company_pair relationship
│ Strategy 4: related_trades table    │ → stored relationships
└─────────────────────────────────────┘
    ↓
Sort by relationship_strength
    ↓
Return top N results
```

### 3. Database Schema

The `related_trades` table stores pre-computed relationships:

```sql
CREATE TABLE related_trades (
    id BIGSERIAL PRIMARY KEY,
    market_id TEXT NOT NULL,
    related_market_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- 'event', 'sector', 'company_pair', 'geographic'
    relationship_strength DECIMAL(5, 4),  -- 0.0 to 1.0
    description TEXT,
    examples TEXT[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 4. On-the-Fly vs Stored Relationships

**On-the-Fly (Current Implementation)**:
- ✅ Fast to implement
- ✅ Always up-to-date
- ✅ No maintenance needed
- ❌ Slower for large datasets
- ❌ Limited entity extraction (heuristic-based)

**Stored Relationships (Future Enhancement)**:
- ✅ Fast queries
- ✅ Can use advanced NLP
- ✅ Can analyze historical trading patterns
- ❌ Requires batch processing
- ❌ Needs periodic updates

**Hybrid Approach (Recommended)**:
- Use on-the-fly for immediate results
- Populate `related_trades` table with high-confidence relationships
- Query stored relationships first, fall back to on-the-fly

## API Endpoints

### 1. `/markets/{market_id}/related`

Get related markets for a specific market.

**Query Parameters**:
- `limit` (int, default=10): Max results
- `relationship_types` (string, optional): Comma-separated types

**Example**:
```bash
GET /markets/517310/related?limit=5&relationship_types=event,sector
```

**Response**:
```json
{
  "source_market": {
    "market_id": "517310",
    "question": "Will Bitcoin hit $100k?",
    "event_title": "Bitcoin price prediction",
    "tag_label": "Crypto"
  },
  "related_markets": [
    {
      "market_id": "517311",
      "question": "Will Bitcoin hit $90k?",
      "relationship_type": "event",
      "relationship_strength": 1.0,
      "description": "Same event: Bitcoin price prediction"
    }
  ],
  "count": 1
}
```

### 2. `/related`

Flexible endpoint accepting `market_id` or `event_title`.

**Query Parameters**:
- `market_id` (string, optional)
- `event_title` (string, optional)
- `limit` (int, default=10)
- `relationship_types` (string, optional)

**Example**:
```bash
GET /related?event_title=Bitcoin%20price%20prediction&limit=10
```

## Implementation Details

### Entity Extraction

Current implementation uses simple keyword matching:

```python
def extract_entities(text: str) -> List[str]:
    """Extract company/entity names from text"""
    # Simple heuristic-based extraction
    # TODO: Enhance with NLP/NER (spaCy, NLTK, etc.)
```

**Future Enhancement**:
- Use Named Entity Recognition (NER) models
- Extract: Companies, People, Locations, Organizations
- Use embeddings for fuzzy matching

### Relationship Strength Calculation

```python
# Event relationship
if same_event_title:
    strength = 1.0

# Sector relationship
if same_tag_label:
    strength = 0.9 if same_event else 0.7

# Company pair
overlap = len(shared_entities)
strength = 0.6 + (overlap * 0.1)  # Max 0.9
```

### Performance Considerations

1. **Indexing**: Ensure indexes on:
   - `markets.event_title`
   - `markets.tag_label`
   - `markets.question` (for text search)
   - `related_trades.market_id`

2. **Caching**: Consider caching results for popular markets

3. **Batch Processing**: For large datasets, pre-compute relationships

## Usage Examples

### Python

```python
from polymarket.get_related_traded import get_related_traded

# By market ID
result = get_related_traded(market_id="517310", limit=10)

# By event title
result = get_related_traded(event_title="Bitcoin price prediction", limit=10)

# Filter by relationship type
result = get_related_traded(
    market_id="517310",
    limit=10,
    relationship_types=["event", "sector"]
)
```

### API

```bash
# Get related markets
curl "http://localhost:8000/markets/517310/related?limit=5"

# Get only event and sector relationships
curl "http://localhost:8000/related?market_id=517310&relationship_types=event,sector"
```

## Future Enhancements

### 1. Advanced Entity Extraction
- Use spaCy or NLTK for NER
- Extract: Companies, People, Locations, Dates
- Fuzzy matching for entity variations

### 2. Price Correlation Analysis
- Analyze historical price movements
- Calculate correlation coefficients
- Store in `trade_correlations` table

### 3. Trading Pattern Analysis
- Identify pairs that trade together
- Detect arbitrage opportunities
- Find hedging relationships

### 4. Machine Learning
- Train models on historical trading data
- Predict relationship strength
- Identify novel relationships

### 5. Real-time Updates
- Stream processing for new markets
- Automatic relationship detection
- Incremental updates to `related_trades` table

## Testing

### Unit Tests

```python
def test_get_related_traded_by_market_id():
    result = get_related_traded(market_id="517310", limit=5)
    assert result["count"] > 0
    assert "source_market" in result
    assert "related_markets" in result

def test_get_related_traded_by_event_title():
    result = get_related_traded(event_title="Bitcoin price", limit=5)
    assert result["count"] > 0

def test_relationship_types_filtering():
    result = get_related_traded(
        market_id="517310",
        relationship_types=["event"]
    )
    for market in result["related_markets"]:
        assert market["relationship_type"] == "event"
```

### Integration Tests

```bash
# Test API endpoint
curl "http://localhost:8000/markets/517310/related?limit=5"

# Test with filters
curl "http://localhost:8000/related?market_id=517310&relationship_types=event,sector"
```

## Migration Checklist

- [x] Create `get_related_traded.py` module
- [x] Implement relationship detection strategies
- [x] Add API endpoints
- [ ] Create batch processing script for `related_trades` table
- [ ] Add entity extraction enhancement (NLP)
- [ ] Add price correlation analysis
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Update documentation

## Performance Benchmarks

**Target Performance**:
- Query time: < 500ms for 10 related markets
- Can handle: 10,000+ markets
- Cache hit rate: > 80% for popular markets

**Optimization Strategies**:
1. Index all query fields
2. Cache frequently accessed markets
3. Batch pre-compute high-confidence relationships
4. Use materialized views for complex queries

## Conclusion

The `get_related_traded` functionality provides a complementary approach to finding related markets, focusing on trading patterns rather than text similarity. The hybrid approach (on-the-fly + stored relationships) provides both flexibility and performance.
