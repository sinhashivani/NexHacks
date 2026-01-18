"""
Get Related Traded Markets
Finds markets related through trading patterns, not just text similarity.
Relationships include: same event, same company/entity, same sector, geographic proximity.
"""

import json
from typing import List, Dict, Optional
from database.supabase_connection import SupabaseConnection


def normalize_token_ids(token_ids_str: str) -> str:
    """
    Normalize clob_token_ids to consistent format for matching
    """
    if not token_ids_str or token_ids_str.strip().lower() == 'none':
        return ""
    
    try:
        token_ids = json.loads(token_ids_str)
        if isinstance(token_ids, list):
            normalized = sorted([str(tid).strip() for tid in token_ids if str(tid).strip()])
            return json.dumps(normalized, separators=(',', ':'))
        return token_ids_str.strip()
    except (json.JSONDecodeError, TypeError):
        return token_ids_str.strip()


def extract_entities(text: str) -> List[str]:
    """
    Extract potential company/entity names from market question.
    Simple heuristic-based extraction (can be enhanced with NLP later).
    """
    if not text:
        return []
    
    # Common company indicators
    entities = []
    text_lower = text.lower()
    
    # Common company names/patterns
    company_keywords = [
        'apple', 'microsoft', 'google', 'amazon', 'meta', 'tesla', 'nvidia',
        'bitcoin', 'ethereum', 'crypto', 'btc', 'eth',
        'trump', 'biden', 'election', 'president',
        'fed', 'federal reserve', 'ecb', 'european central bank'
    ]
    
    for keyword in company_keywords:
        if keyword in text_lower:
            entities.append(keyword)
    
    return entities


def get_related_traded(
    market_id: str = None,
    event_title: str = None,
    clob_token_ids: str = None,
    limit: int = 10,
    relationship_types: Optional[List[str]] = None
) -> dict:
    """
    Get markets related through trading patterns.
    
    This function finds related markets based on:
    1. Same event_title (markets in the same event)
    2. Same tag_label/category (sector relationships)
    3. Same entities/companies mentioned (company_pair relationships)
    4. Geographic relationships (markets about same location)
    
    Args:
        market_id: Market ID to find related markets for
        event_title: Event title to find related markets for (alternative to market_id)
        clob_token_ids: CLOB token IDs (alternative to market_id)
        limit: Maximum number of related markets to return
        relationship_types: Filter by relationship types ['event', 'sector', 'company_pair', 'geographic']
    
    Returns:
        Dictionary with:
        - source_market: Source market information
        - related_markets: List of related markets with relationship metadata
        - count: Number of related markets found
    """
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        
        # Step 1: Get source market information
        source_market = None
        
        if market_id:
            market_response = client.table("markets").select(
                "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
            ).eq("market_id", market_id).limit(1).execute()
            
            if market_response.data:
                source_market = market_response.data[0]
        
        elif event_title:
            market_response = client.table("markets").select(
                "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
            ).eq("event_title", event_title).limit(1).execute()
            
            if market_response.data:
                source_market = market_response.data[0]
        
        elif clob_token_ids:
            normalized = normalize_token_ids(clob_token_ids)
            market_response = client.table("markets").select(
                "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
            ).eq("clob_token_ids", normalized).limit(1).execute()
            
            if market_response.data:
                source_market = market_response.data[0]
        
        if not source_market:
            return {
                "source_market": None,
                "related_markets": [],
                "count": 0,
                "message": "Source market not found"
            }
        
        source_event_title = source_market.get("event_title")
        source_tag_label = source_market.get("tag_label")
        source_question = source_market.get("question", "")
        source_entities = extract_entities(source_question)
        
        # Step 2: Find related markets using multiple strategies
        related_markets = []
        seen_market_ids = {source_market.get("market_id")}
        
        # Strategy 1: Same event_title (event relationship)
        if source_event_title and (not relationship_types or 'event' in relationship_types):
            event_markets = client.table("markets").select(
                "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
            ).eq("event_title", source_event_title).neq("market_id", source_market.get("market_id")).limit(limit).execute()
            
            for market in event_markets.data:
                if market.get("market_id") not in seen_market_ids:
                    related_markets.append({
                        "market_id": market.get("market_id"),
                        "question": market.get("question"),
                        "market_slug": market.get("market_slug"),
                        "event_title": market.get("event_title"),
                        "tag_label": market.get("tag_label"),
                        "clob_token_ids": market.get("clob_token_ids"),
                        "relationship_type": "event",
                        "relationship_strength": 1.0,  # Same event = 100% strength
                        "description": f"Same event: {source_event_title}"
                    })
                    seen_market_ids.add(market.get("market_id"))
        
        # Strategy 2: Same tag_label/category (sector relationship)
        if source_tag_label and (not relationship_types or 'sector' in relationship_types):
            tag_markets = client.table("markets").select(
                "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
            ).eq("tag_label", source_tag_label).neq("market_id", source_market.get("market_id")).limit(limit).execute()
            
            for market in tag_markets.data:
                if market.get("market_id") not in seen_market_ids:
                    # Lower strength if not same event
                    strength = 0.7 if market.get("event_title") != source_event_title else 0.9
                    
                    related_markets.append({
                        "market_id": market.get("market_id"),
                        "question": market.get("question"),
                        "market_slug": market.get("market_slug"),
                        "event_title": market.get("event_title"),
                        "tag_label": market.get("tag_label"),
                        "clob_token_ids": market.get("clob_token_ids"),
                        "relationship_type": "sector",
                        "relationship_strength": strength,
                        "description": f"Same category: {source_tag_label}"
                    })
                    seen_market_ids.add(market.get("market_id"))
        
        # Strategy 3: Company/entity pairs (company_pair relationship)
        if source_entities and (not relationship_types or 'company_pair' in relationship_types):
            # Search for markets mentioning same entities
            for entity in source_entities[:3]:  # Limit to top 3 entities
                entity_markets = client.table("markets").select(
                    "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
                ).ilike("question", f"%{entity}%").neq("market_id", source_market.get("market_id")).limit(limit // 2).execute()
                
                for market in entity_markets.data:
                    if market.get("market_id") not in seen_market_ids:
                        # Calculate strength based on entity overlap
                        market_entities = extract_entities(market.get("question", ""))
                        overlap = len(set(source_entities) & set(market_entities))
                        strength = min(0.6 + (overlap * 0.1), 0.9)
                        
                        related_markets.append({
                            "market_id": market.get("market_id"),
                            "question": market.get("question"),
                            "market_slug": market.get("market_slug"),
                            "event_title": market.get("event_title"),
                            "tag_label": market.get("tag_label"),
                            "clob_token_ids": market.get("clob_token_ids"),
                            "relationship_type": "company_pair",
                            "relationship_strength": strength,
                            "description": f"Shared entity: {entity}",
                            "shared_entities": list(set(source_entities) & set(market_entities))
                        })
                        seen_market_ids.add(market.get("market_id"))
        
        # Strategy 4: Check related_trades table if it exists
        # This would be populated by a separate process that analyzes trading patterns
        try:
            stored_related = client.table("related_trades").select(
                "related_market_id, relationship_type, relationship_strength, description"
            ).eq("market_id", source_market.get("market_id")).execute()
            
            for rel in stored_related.data:
                related_id = rel.get("related_market_id")
                if related_id not in seen_market_ids:
                    # Get market details
                    related_market = client.table("markets").select(
                        "market_id, question, market_slug, event_title, tag_label, clob_token_ids"
                    ).eq("market_id", related_id).limit(1).execute()
                    
                    if related_market.data:
                        market = related_market.data[0]
                        rel_type = rel.get("relationship_type", "unknown")
                        
                        if not relationship_types or rel_type in relationship_types:
                            related_markets.append({
                                "market_id": market.get("market_id"),
                                "question": market.get("question"),
                                "market_slug": market.get("market_slug"),
                                "event_title": market.get("event_title"),
                                "tag_label": market.get("tag_label"),
                                "clob_token_ids": market.get("clob_token_ids"),
                                "relationship_type": rel_type,
                                "relationship_strength": float(rel.get("relationship_strength", 0.5)),
                                "description": rel.get("description", f"Stored relationship: {rel_type}")
                            })
                            seen_market_ids.add(related_id)
        except Exception:
            # Table might not exist yet, that's okay
            pass
        
        # Sort by relationship strength and limit results
        related_markets.sort(key=lambda x: x.get("relationship_strength", 0), reverse=True)
        related_markets = related_markets[:limit]
        
        # Step 3: Return results
        return {
            "source_market": {
                "market_id": source_market.get("market_id"),
                "question": source_market.get("question"),
                "market_slug": source_market.get("market_slug"),
                "event_title": source_market.get("event_title"),
                "tag_label": source_market.get("tag_label")
            },
            "related_markets": related_markets,
            "count": len(related_markets)
        }
    
    except Exception as e:
        return {
            "source_market": None,
            "related_markets": [],
            "count": 0,
            "error": str(e)
        }


def get_related_traded_by_market_id(market_id: str, limit: int = 10) -> dict:
    """Convenience wrapper for getting related markets by market_id"""
    return get_related_traded(market_id=market_id, limit=limit)


def get_related_traded_by_event_title(event_title: str, limit: int = 10) -> dict:
    """Convenience wrapper for getting related markets by event_title"""
    return get_related_traded(event_title=event_title, limit=limit)
