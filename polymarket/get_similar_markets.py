"""
Get Similar Markets by Event Title
Given an exact event_title, finds the top 5 most similar markets ordered by cosine similarity
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
        # Parse JSON array and re-serialize with consistent formatting
        token_ids = json.loads(token_ids_str)
        if isinstance(token_ids, list):
            # Sort and normalize
            normalized = sorted([str(tid).strip() for tid in token_ids if str(tid).strip()])
            return json.dumps(normalized, separators=(',', ':'))
        return token_ids_str.strip()
    except (json.JSONDecodeError, TypeError):
        return token_ids_str.strip()


def get_similar_by_event_title(event_title: str, limit: int = 5) -> dict:
    """
    Given an exact event_title, this method:
    1) looks up the corresponding clob_token_ids in the markets table,
    2) uses those token IDs to query the similarity_scores table,
    3) fetches the top 5 most similar markets ordered by cosine similarity,
    4) enriches each result with human-readable metadata (title and question),
    and returns this event's clob_token_ids and similar markets
    
    Args:
        event_title: Exact event title to search for
        limit: Number of similar markets to return (default: 5)
    
    Returns:
        Dictionary with:
        - event_title: The searched event title
        - clob_token_ids: List of token IDs for this event
        - similar_markets: List of similar markets with metadata
    """
    try:
        # Connect to Supabase
        conn = SupabaseConnection()
        client = conn.get_client()
        
        # Step 1: Find markets with this event_title and get their clob_token_ids
        markets_response = client.table("markets").select(
            "clob_token_ids, question, market_id, market_slug"
        ).eq("event_title", event_title).execute()
        
        if not markets_response.data:
            return {
                "event_title": event_title,
                "clob_token_ids": [],
                "similar_markets": [],
                "message": "No markets found for this event title"
            }
        
        # Collect all unique clob_token_ids from markets with this event_title
        source_token_ids_set = set()
        event_markets = []
        
        for market in markets_response.data:
            clob_token_ids_str = market.get("clob_token_ids")
            if clob_token_ids_str:
                normalized = normalize_token_ids(clob_token_ids_str)
                if normalized:
                    source_token_ids_set.add(normalized)
                    event_markets.append({
                        "market_id": market.get("market_id"),
                        "question": market.get("question"),
                        "market_slug": market.get("market_slug"),
                        "clob_token_ids": normalized
                    })
        
        if not source_token_ids_set:
            return {
                "event_title": event_title,
                "clob_token_ids": [],
                "similar_markets": [],
                "message": "No valid clob_token_ids found for this event"
            }
        
        # Step 2: Query similarity_scores table for similar markets
        # Get all similarity records where source matches any of our token IDs
        all_similarities = []
        
        for source_token_ids in source_token_ids_set:
            similarities_response = client.table("similarity_scores").select(
                "neighbor_clob_token_ids, cosine_similarity"
            ).eq("source_clob_token_ids", source_token_ids).order(
                "cosine_similarity", desc=True
            ).limit(limit * 2).execute()  # Get more than needed to account for duplicates
            
            for sim in similarities_response.data:
                all_similarities.append({
                    "neighbor_clob_token_ids": sim.get("neighbor_clob_token_ids"),
                    "cosine_similarity": float(sim.get("cosine_similarity", 0))
                })
        
        # Sort by similarity and get top results
        all_similarities.sort(key=lambda x: x["cosine_similarity"], reverse=True)
        
        # Deduplicate by neighbor_clob_token_ids and get top limit
        seen_neighbors = set()
        top_similarities = []
        
        for sim in all_similarities:
            neighbor_ids = sim["neighbor_clob_token_ids"]
            if neighbor_ids not in seen_neighbors and neighbor_ids not in source_token_ids_set:
                seen_neighbors.add(neighbor_ids)
                top_similarities.append(sim)
                if len(top_similarities) >= limit:
                    break
        
        # Step 3: Enrich with market metadata
        similar_markets = []
        
        for sim in top_similarities:
            neighbor_ids = sim["neighbor_clob_token_ids"]
            
            # Find markets with matching clob_token_ids
            neighbor_markets_response = client.table("markets").select(
                "market_id, question, market_slug, event_title, tag_label"
            ).eq("clob_token_ids", neighbor_ids).limit(1).execute()
            
            if neighbor_markets_response.data:
                market = neighbor_markets_response.data[0]
                similar_markets.append({
                    "market_id": market.get("market_id"),
                    "question": market.get("question"),
                    "market_slug": market.get("market_slug"),
                    "event_title": market.get("event_title"),
                    "tag_label": market.get("tag_label"),
                    "clob_token_ids": neighbor_ids,
                    "cosine_similarity": sim["cosine_similarity"]
                })
            else:
                # Market not found in database, but we have similarity score
                similar_markets.append({
                    "market_id": None,
                    "question": None,
                    "market_slug": None,
                    "event_title": None,
                    "tag_label": None,
                    "clob_token_ids": neighbor_ids,
                    "cosine_similarity": sim["cosine_similarity"]
                })
        
        # Step 4: Return results
        return {
            "event_title": event_title,
            "clob_token_ids": list(source_token_ids_set),
            "event_markets": event_markets,
            "similar_markets": similar_markets,
            "count": len(similar_markets)
        }
    
    except Exception as e:
        return {
            "event_title": event_title,
            "clob_token_ids": [],
            "similar_markets": [],
            "error": str(e)
        }
