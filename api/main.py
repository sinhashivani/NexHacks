import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to Python path so we can import from root-level modules
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Load environment variables from root .env file
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: load from current directory or environment
    load_dotenv()

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

from polymarket.get_markets_data import ui
from polymarket.get_similar_markets import get_similar_by_event_title
from polymarket.get_related_traded import get_related_traded, get_related_traded_by_market_id, get_related_traded_by_event_title
from polymarket.news import fetch_news
from services.trending import TrendingService
from services.polymarket_api import PolymarketAPIService

# Import advanced API clients
from api.clients.gamma_client import GammaClient
from api.clients.clob_client import ClobClient
from api.clients.gemini_client import GeminiClient

app = FastAPI(
    title="NexHacks Polymarket Correlation Tool",
    version="1.0.0",
    description="API for Polymarket correlation, trending, and parlay suggestions"
)

# Request logging middleware to add PNA header for Chrome Private Network Access
# This MUST come BEFORE CORS middleware so PNA header is added to CORS responses
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        
        # #region agent log (only in local dev, not on Vercel)
        if os.getenv("VERCEL") is None:  # Only log locally
            import json
            try:
                debug_log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
                if debug_log_path.parent.exists():
                    with open(debug_log_path, 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"api/main.py:middleware","message":"Incoming request","data":{"method":request.method,"url":str(request.url),"origin":request.headers.get("origin")},"timestamp":int(time.time()*1000)})+"\n")
            except: pass
        # #endregion
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add Chrome Private Network Access header (required for HTTPS->localhost)
        # This header tells Chrome it's safe to allow HTTPS pages to access localhost
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        
        # #region agent log (only in local dev)
        if os.getenv("VERCEL") is None:
            import json
            try:
                debug_log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
                if debug_log_path.parent.exists():
                    with open(debug_log_path, 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"api/main.py:middleware","message":"Request completed","data":{"status_code":response.status_code,"process_time":process_time},"timestamp":int(time.time()*1000)})+"\n")
            except: pass
        # #endregion
        
        return response

app.add_middleware(LoggingMiddleware)

# Configure CORS middleware to allow requests from Chrome extensions
# This comes AFTER logging middleware so PNA header is preserved
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Chrome extensions can come from any domain)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers including Access-Control-Allow-Private-Network
)

# Initialize services (lazy-loaded to avoid import-time failures)
_trending_service: Optional[TrendingService] = None
_polymarket_api: Optional[PolymarketAPIService] = None

# Initialize advanced API clients (lazy-loaded singletons)
_gamma_client: Optional[GammaClient] = None
_clob_client: Optional[ClobClient] = None
_gemini_client: Optional[GeminiClient] = None

def get_trending_service() -> TrendingService:
    """Get or create TrendingService instance"""
    global _trending_service
    if _trending_service is None:
        _trending_service = TrendingService()
    return _trending_service

def get_polymarket_api() -> PolymarketAPIService:
    """Get or create PolymarketAPIService instance"""
    global _polymarket_api
    if _polymarket_api is None:
        _polymarket_api = PolymarketAPIService()
    return _polymarket_api

def get_gamma_client() -> GammaClient:
    """Get or create Gamma API client"""
    global _gamma_client
    if _gamma_client is None:
        _gamma_client = GammaClient()
    return _gamma_client

def get_clob_client() -> ClobClient:
    """Get or create CLOB API client"""
    global _clob_client
    if _clob_client is None:
        _clob_client = ClobClient()
    return _clob_client

def get_gemini_client() -> GeminiClient:
    """Get or create Gemini AI client"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

@app.get("/")
def root():
    """Root endpoint with API information"""
    # #region agent log (only in local dev)
    if os.getenv("VERCEL") is None:
        import json
        try:
            debug_log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
            if debug_log_path.parent.exists():
                with open(debug_log_path, 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"api/main.py:70","message":"Root endpoint called","data":{},"timestamp":int(__import__('time').time()*1000)})+"\n")
        except: pass
    # #endregion
    return {
        "name": "NexHacks Polymarket API",
        "version": "1.0.0",
        "endpoints": {
            "trending": "/markets/trending",
            "ui": "/ui"
        }
    }

@app.get("/test-cors")
def test_cors():
    """Test endpoint to verify CORS is working"""
    # #region agent log (only in local dev)
    if os.getenv("VERCEL") is None:
        import json
        try:
            debug_log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
            if debug_log_path.parent.exists():
                with open(debug_log_path, 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"api/main.py:142","message":"CORS test endpoint called","data":{},"timestamp":int(__import__('time').time()*1000)})+"\n")
        except: pass
    # #endregion
    return {"status": "ok", "cors": "enabled", "message": "CORS test successful"}

@app.get("/favicon.ico")
@app.get("/favicon.png")
@app.head("/favicon.ico")
@app.head("/favicon.png")
def favicon():
    """Handle favicon requests to prevent 404 errors in logs"""
    # Return 204 No Content - standard response for missing favicons
    return Response(status_code=204)

@app.get("/markets/trending")
def get_trending_markets(
    category: Optional[str] = Query(None, description="Filter by category (e.g., politics, sports, tech)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    min_score: float = Query(0.0, ge=0.0, le=1.0, description="Minimum trending score")
):
    """
    Get trending/popular markets ranked by popularity
    
    Returns markets sorted by trending score based on:
    - Open interest
    - 24-hour volume
    - Liquidity
    """
    try:
        service = get_trending_service()
        markets = service.get_trending_markets(
            category=category,
            limit=limit,
            min_score=min_score
        )
        
        # #region agent log (only in local dev)
        if os.getenv("VERCEL") is None:
            import json
            try:
                debug_log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
                if debug_log_path.parent.exists():
                    with open(debug_log_path, 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"api/main.py:108","message":"Trending markets fetched successfully","data":{"count":len(markets)},"timestamp":int(__import__('time').time()*1000)})+"\n")
            except: pass
        # #endregion
        return {
            "count": len(markets),
            "markets": markets
        }
    
    except Exception as e:
        # #region agent log (only in local dev)
        if os.getenv("VERCEL") is None:
            import json
            try:
                debug_log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
                if debug_log_path.parent.exists():
                    with open(debug_log_path, 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"api/main.py:194","message":"Error in trending endpoint","data":{"error":str(e)},"timestamp":int(__import__('time').time()*1000)})+"\n")
            except: pass
        # #endregion
        raise HTTPException(status_code=500, detail=f"Error fetching trending markets: {str(e)}")


@app.get("/markets/trending/refresh")
def refresh_trending_data(
    limit: int = Query(100, ge=1, le=500, description="Number of markets to fetch from Polymarket")
):
    """
    Refresh market metrics from Polymarket API
    
    This endpoint fetches latest data from Polymarket and updates the market_metrics table.
    Call this periodically to keep trending data fresh.
    """
    try:
        api_service = get_polymarket_api()
        updated = api_service.fetch_and_update_metrics(limit=limit)
        return {
            "success": True,
            "markets_updated": updated,
            "message": f"Updated metrics for {updated} markets"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing metrics: {str(e)}")


@app.get("/ui")
def get_ui(token_id: str = Query(..., description="CLOB token id")):
    """Get market UI data by CLOB token ID (existing endpoint)"""
    try:
        data = ui(token_id.strip())
        if not data:
            raise HTTPException(status_code=404, detail="Market not found")
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar")
async def get_similar(
    event_title: str = Query(..., description="Market question to search for"),
    use_cosine: bool = Query(True, description="Use cosine similarity scores"),
    min_similarity: float = Query(0.5, description="Minimum cosine similarity threshold"),
    use_embeddings: bool = Query(True, description="Use embedding-based semantic search (recommended)")
):
    """
    Get similar markets using multiple strategies (in priority order):
    1. Embedding-based semantic search (if use_embeddings=True) - MOST ACCURATE
    2. Cosine similarity from similarity_scores table
    3. Tag-based matching (markets with same tag_label)
    4. Fuzzy text matching on question field
    
    Returns markets sorted by similarity score.
    """
    import logging
    import json
    import re
    import numpy as np
    from database.supabase_connection import SupabaseConnection
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def cosine_similarity(vec1, vec2) -> float:
        """Compute cosine similarity between two vectors"""
        try:
            # Handle both list and numpy array inputs
            v1 = np.array(vec1, dtype=np.float32)
            v2 = np.array(vec2, dtype=np.float32)
            
            # Ensure same length
            if len(v1) != len(v2):
                return 0.0
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = float(dot_product / (norm1 * norm2))
            # Ensure result is between -1 and 1 (cosine similarity range)
            return max(-1.0, min(1.0, similarity))
        except Exception as e:
            logger.warning(f"[SIMILAR] Error computing cosine similarity: {e}")
            return 0.0
    
    def normalize_token_ids(token_ids):
        """Normalize clob_token_ids to consistent format for matching"""
        if not token_ids:
            return None
        try:
            if isinstance(token_ids, str):
                token_list = json.loads(token_ids)
            else:
                token_list = token_ids
            
            if isinstance(token_list, list):
                # Sort and normalize
                normalized = sorted([str(tid).strip() for tid in token_list if str(tid).strip()])
                return json.dumps(normalized, separators=(',', ':'))
            return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    try:
        logger.info(f"[SIMILAR] Starting search for: '{event_title}'")
        logger.info(f"[SIMILAR] use_embeddings={use_embeddings}, use_cosine={use_cosine}, min_similarity={min_similarity}")
        
        conn = SupabaseConnection()
        client = conn.get_client()
        
        similar_markets = []
        source_market = None
        
        # Strategy 0: Embedding-based semantic search (MOST ACCURATE)
        if use_embeddings:
            logger.info("[SIMILAR] Strategy 0: Embedding-based semantic search...")
            
            # Find source market by matching the scraped title
            source_search = f"%{event_title}%"
            source_markets = client.table("markets").select(
                "market_id, question, market_slug, tag_label, clob_token_ids, embedding"
            ).ilike("question", source_search).limit(1).execute()
            
            if source_markets.data:
                source_market = source_markets.data[0]
                source_embedding = source_market.get('embedding')
                
                logger.info(f"[SIMILAR] Found source market: {source_market['question']}")
                logger.info(f"[SIMILAR] Source has embedding: {source_embedding is not None}")
                
                if source_embedding:
                    # Use pgvector cosine distance to find similar markets
                    # Supabase/PostgreSQL pgvector uses <=> operator for cosine distance
                    # We'll use RPC function or raw SQL for vector similarity search
                    try:
                        # Query using pgvector cosine distance
                        # Note: Supabase Python client doesn't directly support vector operators,
                        # so we'll use a raw SQL query via RPC or execute raw SQL
                        from database.supabase_connection import get_connection
                        db_conn = get_connection()
                        
                        if db_conn:
                            # Convert embedding to string format for SQL
                            if isinstance(source_embedding, list):
                                embedding_str = '[' + ','.join(map(str, source_embedding)) + ']'
                            else:
                                embedding_str = str(source_embedding)
                            
                            # Use pgvector cosine distance operator (<=>)
                            # 1 - (embedding <=> query_embedding) gives cosine similarity
                            query = f"""
                            SELECT 
                                market_id,
                                question,
                                market_slug,
                                tag_label,
                                clob_token_ids,
                                1 - (embedding <=> '{embedding_str}'::vector) as similarity
                            FROM markets
                            WHERE embedding IS NOT NULL
                                AND market_id != %s
                            ORDER BY embedding <=> '{embedding_str}'::vector
                            LIMIT 20
                            """
                            
                            import psycopg2.extras
                            cursor = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                            cursor.execute(query, (source_market['market_id'],))
                            embedding_results = cursor.fetchall()
                            cursor.close()
                            
                            logger.info(f"[SIMILAR] Found {len(embedding_results)} similar markets via embeddings")
                            
                            for row in embedding_results:
                                similarity = float(row['similarity'])
                                if similarity >= min_similarity:
                                    similar_markets.append({
                                        "market_id": row['market_id'],
                                        "question": row['question'],
                                        "market_slug": row.get('market_slug'),
                                        "tag_label": row.get('tag_label'),
                                        "cosine_similarity": similarity,
                                        "match_type": "embedding_similarity"
                                    })
                                    
                                    if len(similar_markets) <= 3:
                                        logger.info(f"[SIMILAR] Added embedding match: {row['question'][:80]}... (similarity={similarity:.4f})")
                        else:
                            logger.warning("[SIMILAR] Could not get database connection for vector search")
                    except Exception as e:
                        logger.warning(f"[SIMILAR] Error in embedding search: {e}")
                        logger.info("[SIMILAR] Falling back to other strategies...")
                else:
                    logger.info("[SIMILAR] Source market has no embedding, skipping embedding search")
            else:
                logger.info("[SIMILAR] Source market not found, skipping embedding search")
        
        # Strategy 1: Find source market and use cosine similarity from similarity_scores table
        if use_cosine:
            logger.info("[SIMILAR] Strategy 1: Looking for source market...")
            
            # Find source market by fuzzy matching first
            source_search = f"%{event_title}%"
            source_markets = client.table("markets").select(
                "market_id, question, market_slug, tag_label, clob_token_ids"
            ).ilike("question", source_search).limit(1).execute()
            
            if source_markets.data:
                source_market = source_markets.data[0]
                logger.info(f"[SIMILAR] Found source market: {source_market['question']}")
                logger.info(f"[SIMILAR] Source market_id: {source_market['market_id']}")
                logger.info(f"[SIMILAR] Source tag_label: {source_market.get('tag_label')}")
                
                clob_ids = source_market.get('clob_token_ids')
                if clob_ids:
                    try:
                        # Normalize the clob_token_ids
                        clob_ids_json = normalize_token_ids(clob_ids)
                        
                        if clob_ids_json:
                            logger.info(f"[SIMILAR] Normalized clob_ids: {clob_ids_json[:100]}...")
                            
                            # Query similarity_scores table
                            logger.info("[SIMILAR] Querying similarity_scores table...")
                            similarity_results = client.table("similarity_scores").select(
                                "neighbor_clob_token_ids, cosine_similarity"
                            ).eq("source_clob_token_ids", clob_ids_json).gte(
                                "cosine_similarity", min_similarity
                            ).order("cosine_similarity", desc=True).limit(20).execute()
                            
                            logger.info(f"[SIMILAR] Found {len(similarity_results.data)} similarity scores")
                            
                            # Get market details for similar markets
                            for sim in similarity_results.data:
                                neighbor_ids = sim['neighbor_clob_token_ids']
                                cosine_sim = float(sim['cosine_similarity'])
                                
                                # Normalize neighbor_ids for matching
                                neighbor_ids_normalized = normalize_token_ids(neighbor_ids)
                                
                                # Find market with these clob_token_ids (try both normalized and original)
                                neighbor_market = None
                                if neighbor_ids_normalized:
                                    neighbor_market_result = client.table("markets").select(
                                        "market_id, question, market_slug, tag_label"
                                    ).eq("clob_token_ids", neighbor_ids_normalized).limit(1).execute()
                                    if neighbor_market_result.data:
                                        neighbor_market = neighbor_market_result.data[0]
                                
                                # Fallback: try original format
                                if not neighbor_market:
                                    neighbor_market_result = client.table("markets").select(
                                        "market_id, question, market_slug, tag_label"
                                    ).eq("clob_token_ids", neighbor_ids).limit(1).execute()
                                    if neighbor_market_result.data:
                                        neighbor_market = neighbor_market_result.data[0]
                                
                                if neighbor_market:
                                    # Skip if it's the same market
                                    if neighbor_market["market_id"] != source_market["market_id"]:
                                        similar_markets.append({
                                            "market_id": neighbor_market["market_id"],
                                            "question": neighbor_market["question"],
                                            "market_slug": neighbor_market.get("market_slug"),
                                            "tag_label": neighbor_market.get("tag_label"),
                                            "cosine_similarity": cosine_sim,
                                            "match_type": "cosine_similarity"
                                        })
                                        
                                        if len(similar_markets) <= 3:
                                            logger.info(f"[SIMILAR] Added similar market: {neighbor_market['question'][:80]}... (cosine={cosine_sim:.4f})")
                            
                            logger.info(f"[SIMILAR] Total similar markets from cosine: {len(similar_markets)}")
                        else:
                            logger.warning("[SIMILAR] Could not normalize clob_token_ids")
                        
                    except Exception as e:
                        logger.warning(f"[SIMILAR] Error processing cosine similarity: {e}")
        
        # Strategy 2: Tag-based matching (find markets with same tag_label)
        # This is CRITICAL for relevance - prioritize same category
        if len(similar_markets) < 10 and source_market:
            tag_label = source_market.get('tag_label')
            if tag_label:
                logger.info(f"[SIMILAR] Strategy 2: Tag-based search (tag: {tag_label})...")
                tag_results = client.table("markets").select(
                    "market_id, question, market_slug, tag_label"
                ).eq("tag_label", tag_label).neq(
                    "market_id", source_market["market_id"]
                ).limit(20).execute()  # Get more for better selection
                
                logger.info(f"[SIMILAR] Tag search found {len(tag_results.data)} results")
                
                existing_ids = {m["market_id"] for m in similar_markets}
                for market in tag_results.data:
                    if market["market_id"] not in existing_ids:
                        similar_markets.append({
                            "market_id": market["market_id"],
                            "question": market["question"],
                            "market_slug": market.get("market_slug"),
                            "tag_label": market.get("tag_label"),
                            "cosine_similarity": 0.75,  # Higher score for tag match
                            "match_type": "tag_match"
                        })
                        
                        if len(similar_markets) <= 3:
                            logger.info(f"[SIMILAR] Added tag match: {market['question'][:80]}...")
        
        # Strategy 3: Improved fuzzy text search with better keyword filtering
        if len(similar_markets) < 10:
            logger.info("[SIMILAR] Strategy 3: Improved fuzzy text search...")
            
            # Extract meaningful keywords (filter out common/stop words and years)
            stop_words = {'will', 'the', 'be', 'by', 'in', 'on', 'at', 'for', 'to', 'of', 'a', 'an', 'and', 'or', 'but', 'if', 'as', 'out', 'with', 'from', 'this', 'that', 'these', 'those'}
            all_words = re.findall(r'\b\w{3,}\b', event_title.lower())
            # Filter out years (4-digit numbers like 2026, 2025, etc.) and stop words
            keywords = [w for w in all_words if w not in stop_words and len(w) >= 4 and not (w.isdigit() and len(w) == 4)]
            
            # Use the source tag_label we already extracted
            if keywords:
                logger.info(f"[SIMILAR] Extracted keywords: {keywords[:5]}")
                
                # Require at least 2 keywords to match for better relevance
                # Build query that requires multiple keyword matches
                if len(keywords) >= 2:
                    # Use top 3-4 keywords, require at least 2 matches
                    search_keywords = keywords[:4]
                    search_terms = [f"%{kw}%" for kw in search_keywords]
                    
                    # Build query: markets containing multiple keywords
                    query = client.table("markets").select(
                        "market_id, question, market_slug, tag_label"
                    )
                    
                    # If source has tag_label, filter by it first
                    if tag_label:
                        query = query.eq("tag_label", tag_label)
                    
                    # Then filter by keywords (OR condition)
                    query = query.or_(",".join([f"question.ilike.{term}" for term in search_terms]))
                    
                    # Exclude source market
                    if source_market:
                        query = query.neq("market_id", source_market["market_id"])
                    
                    fuzzy_results = query.limit(30).execute()  # Get more to filter better
                    
                    logger.info(f"[SIMILAR] Fuzzy search found {len(fuzzy_results.data)} results")
                    
                    existing_ids = {m["market_id"] for m in similar_markets}
                    if source_market:
                        existing_ids.add(source_market["market_id"])
                    
                    # First pass: Require 2+ keyword matches (high relevance)
                    for market in fuzzy_results.data:
                        if market["market_id"] not in existing_ids:
                            question_lower = market["question"].lower()
                            keyword_matches = sum(1 for kw in search_keywords if kw in question_lower)
                            
                            if keyword_matches >= 2:
                                base_score = 0.55
                                tag_bonus = 0.15 if market.get("tag_label") == source_tag_label else 0.0
                                keyword_bonus = (keyword_matches / len(search_keywords)) * 0.1
                                similarity_score = min(0.8, base_score + tag_bonus + keyword_bonus)
                                
                                similar_markets.append({
                                    "market_id": market["market_id"],
                                    "question": market["question"],
                                    "market_slug": market.get("market_slug"),
                                    "tag_label": market.get("tag_label"),
                                    "cosine_similarity": similarity_score,
                                    "match_type": "text_fuzzy"
                                })
                                
                                if len(similar_markets) <= 3:
                                    logger.info(f"[SIMILAR] Added fuzzy match (keywords={keyword_matches}): {market['question'][:80]}...")
                    
                    # Second pass: If not enough results, allow 1 keyword match (but prioritize tag matches)
                    if len(similar_markets) < 5:
                        logger.info("[SIMILAR] Not enough 2+ keyword matches, allowing 1 keyword match...")
                        for market in fuzzy_results.data:
                            if market["market_id"] not in existing_ids:
                                question_lower = market["question"].lower()
                                keyword_matches = sum(1 for kw in search_keywords if kw in question_lower)
                                
                                # Allow 1 match, but STRICTLY prioritize same tag
                                if keyword_matches >= 1:
                                    # Only include if same tag OR if we really need more results (and no tag set)
                                    if market.get("tag_label") == source_tag_label or (len(similar_markets) < 3 and not source_tag_label):
                                        base_score = 0.5 if keyword_matches == 1 else 0.55
                                        tag_bonus = 0.2 if market.get("tag_label") == tag_label else 0.0
                                        similarity_score = min(0.7, base_score + tag_bonus)
                                        
                                        similar_markets.append({
                                            "market_id": market["market_id"],
                                            "question": market["question"],
                                            "market_slug": market.get("market_slug"),
                                            "tag_label": market.get("tag_label"),
                                            "cosine_similarity": similarity_score,
                                            "match_type": "text_fuzzy"
                                        })
                                        
                                        if len(similar_markets) <= 3:
                                            logger.info(f"[SIMILAR] Added 1-keyword match (tag={market.get('tag_label')}): {market['question'][:80]}...")
                                        
                                        if len(similar_markets) >= 10:
                                            break
                    
                    # Third pass: If still not enough and we filtered by tag, try without tag filter
                    if len(similar_markets) < 5 and source_tag_label:
                        logger.info("[SIMILAR] Not enough tag-filtered results, trying broader search...")
                        broader_query = client.table("markets").select(
                            "market_id, question, market_slug, tag_label"
                        ).or_(",".join([f"question.ilike.{term}" for term in search_terms[:2]]))
                        
                        if source_market:
                            broader_query = broader_query.neq("market_id", source_market["market_id"])
                        
                        broader_results = broader_query.limit(20).execute()
                        
                        for market in broader_results.data:
                            if market["market_id"] not in existing_ids:
                                question_lower = market["question"].lower()
                                keyword_matches = sum(1 for kw in search_keywords[:2] if kw in question_lower)
                                
                                # Require at least 2 matches for cross-tag results
                                if keyword_matches >= 2:
                                    similar_markets.append({
                                        "market_id": market["market_id"],
                                        "question": market["question"],
                                        "market_slug": market.get("market_slug"),
                                        "tag_label": market.get("tag_label"),
                                        "cosine_similarity": 0.6,  # Lower score for cross-tag matches
                                        "match_type": "text_fuzzy"
                                    })
                                    
                                    if len(similar_markets) >= 10:
                                        break
        
        # Sort by cosine similarity
        similar_markets.sort(key=lambda x: x.get("cosine_similarity", 0), reverse=True)
        
        # Remove duplicates (keep highest score)
        seen_ids = {}
        deduplicated = []
        for market in similar_markets:
            market_id = market["market_id"]
            if market_id not in seen_ids or market["cosine_similarity"] > seen_ids[market_id]["cosine_similarity"]:
                if market_id in seen_ids:
                    deduplicated.remove(seen_ids[market_id])
                seen_ids[market_id] = market
                deduplicated.append(market)
        
        similar_markets = deduplicated[:15]  # Limit to top 15
        
        logger.info(f"[SIMILAR] === FINAL RESULTS ===")
        logger.info(f"[SIMILAR] Total similar markets: {len(similar_markets)}")
        for idx, m in enumerate(similar_markets[:5]):
            logger.info(f"[SIMILAR]   #{idx+1}: {m['question'][:60]}... (score={m['cosine_similarity']:.4f}, type={m['match_type']})")
        
        return JSONResponse(content={
            "event_title": event_title,
            "similar_markets": similar_markets,
            "count": len(similar_markets),
            "strategy_used": "cosine_similarity" if any(m.get("match_type") == "cosine_similarity" for m in similar_markets) else ("tag_match" if any(m.get("match_type") == "tag_match" for m in similar_markets) else "text_fuzzy")
        })
        
    except Exception as e:
        logger.error(f"[SIMILAR] ERROR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/markets/{market_id}/related")
def get_related_markets(
    market_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of related markets"),
    relationship_types: Optional[str] = Query(None, description="Comma-separated relationship types: event,sector,company_pair,geographic")
):
    """
    Get markets related through trading patterns.
    
    Finds related markets based on:
    - Same event_title (event relationship)
    - Same tag_label/category (sector relationship)
    - Same entities/companies (company_pair relationship)
    - Stored relationships in related_trades table
    
    Different from /similar which uses text similarity.
    """
    try:
        types_list = None
        if relationship_types:
            types_list = [t.strip() for t in relationship_types.split(",")]
        
        data = get_related_traded(market_id=market_id, limit=limit, relationship_types=types_list)
        if not data or data.get("count") == 0:
            return JSONResponse(content=data)  # Return empty result, not 404
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/related")
def get_related(
    market_id: Optional[str] = Query(None, description="Market ID"),
    event_title: Optional[str] = Query(None, description="Event title"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of related markets"),
    relationship_types: Optional[str] = Query(None, description="Comma-separated relationship types")
):
    """
    Get related traded markets (flexible query by market_id or event_title).
    
    This endpoint finds markets related through trading patterns:
    - Same event (markets in the same event)
    - Same sector/category
    - Same companies/entities
    - Geographic relationships
    """
    try:
        if not market_id and not event_title:
            raise HTTPException(status_code=400, detail="Either market_id or event_title must be provided")
        
        types_list = None
        if relationship_types:
            types_list = [t.strip() for t in relationship_types.split(",")]
        
        data = get_related_traded(
            market_id=market_id,
            event_title=event_title,
            limit=limit,
            relationship_types=types_list
        )
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news")
def get_news(
    question: str = Query(..., description="Market question to search for news")
):
    """
    Get recent news articles related to a market question.

    Uses GNews API to find relevant articles from the past 30 days.
    """
    try:
        articles = fetch_news(question.strip())
        return JSONResponse(content={
            "question": question,
            "count": len(articles),
            "articles": articles
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")


# ============================================================================
# ADVANCED API ENDPOINTS (Gamma, CLOB, Gemini AI)
# ============================================================================

@app.get("/gamma/market/{slug}")
async def get_live_market(slug: str):
    """
    Get live market data from Polymarket's official Gamma API.
    
    This endpoint provides real-time market information directly from Polymarket,
    including current prices, volumes, and market status.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        gamma = get_gamma_client()
        market = await gamma.get_market_by_slug(slug)
        
        if not market:
            raise HTTPException(status_code=404, detail=f"Market not found: {slug}")
        
        logger.info(f"[Gamma API] Fetched live market: {slug}")
        return JSONResponse(content=market)
    
    except Exception as e:
        logger.error(f"[Gamma API] Error fetching market {slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching live market: {str(e)}")


@app.get("/gamma/tags")
async def get_gamma_tags(limit: int = Query(100, ge=1, le=500)):
    """
    Get all available tags/categories from Polymarket's Gamma API.
    
    Tags include: Politics, Sports, Crypto, Business, Science, Pop Culture, etc.
    """
    try:
        gamma = get_gamma_client()
        tags = await gamma.get_tags(limit=limit)
        
        return JSONResponse(content={
            "count": len(tags),
            "tags": tags
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tags: {str(e)}")


@app.get("/gamma/events/by-tag/{tag_id}")
async def get_events_by_tag(
    tag_id: int,
    active: bool = Query(True, description="Include active markets"),
    closed: bool = Query(False, description="Include closed markets"),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get markets/events by tag ID from Gamma API.
    
    Use /gamma/tags to discover available tag IDs.
    """
    try:
        gamma = get_gamma_client()
        events = await gamma.get_events_by_tag(
            tag_id=tag_id,
            active=active,
            closed=closed,
            limit=limit
        )
        
        return JSONResponse(content={
            "tag_id": tag_id,
            "count": len(events),
            "events": events
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@app.get("/clob/price/{token_id}")
async def get_live_price(token_id: str):
    """
    Get current live price for a CLOB token ID.
    
    CLOB (Central Limit Order Book) provides real-time price data for all markets.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        clob = get_clob_client()
        price = await clob.get_current_price(token_id)
        
        if price is None:
            raise HTTPException(status_code=404, detail=f"Price not found for token: {token_id}")
        
        logger.info(f"[CLOB API] Fetched live price for {token_id}: {price}")
        
        return JSONResponse(content={
            "token_id": token_id,
            "price": price,
            "timestamp": "now"
        })
    
    except Exception as e:
        logger.error(f"[CLOB API] Error fetching price for {token_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching live price: {str(e)}")


@app.get("/clob/price-history/{token_id}")
async def get_price_history(
    token_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history")
):
    """
    Get price history for a CLOB token ID.
    
    Returns historical price data for correlation analysis and charting.
    """
    try:
        clob = get_clob_client()
        history = await clob.get_price_history_window(token_id, days=days)
        
        return JSONResponse(content={
            "token_id": token_id,
            "days": days,
            "data_points": len(history),
            "history": history
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price history: {str(e)}")


@app.get("/ai/similar")
async def get_ai_similar_markets(
    event_title: str = Query(..., description="Market question to find similar markets for"),
    use_cosine: bool = Query(True, description="Use cosine similarity scores"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    use_ai_ranking: bool = Query(True, description="Use Gemini AI to rank results"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Get similar markets with optional AI-powered ranking.
    
    This enhanced endpoint:
    1. Uses cosine similarity from your database (fast)
    2. Optionally ranks results using Gemini AI (smart)
    3. Considers semantic meaning, not just keywords
    
    Set use_ai_ranking=true for best results (requires GEMINI_API_KEY).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[AI Similar] ========================================")
    logger.info(f"[AI Similar] Query: {event_title}")
    logger.info(f"[AI Similar] AI Ranking: {use_ai_ranking}")
    logger.info(f"[AI Similar] ========================================")
    
    try:
        from database.supabase_connection import SupabaseConnection
        supabase_conn = SupabaseConnection()
        client = supabase_conn.get_client()
        
        # Step 1: Find source market using fuzzy matching
        fuzzy_query = f"%{event_title}%"
        source_result = client.table("markets").select(
            "question, clob_token_ids, market_slug"
        ).ilike("question", fuzzy_query).limit(1).execute()
        
        if not source_result.data:
            logger.warning(f"[AI Similar] No source market found for: {event_title}")
            raise HTTPException(status_code=404, detail="Source market not found")
        
        source_market = source_result.data[0]
        source_token_ids = source_market.get("clob_token_ids")
        
        logger.info(f"[AI Similar] Found source: {source_market.get('question')}")
        logger.info(f"[AI Similar] Token IDs: {source_token_ids}")
        
        if not source_token_ids:
            logger.warning(f"[AI Similar] No token IDs for source market")
            raise HTTPException(status_code=404, detail="Source market has no token IDs")
        
        # Step 2: Get similar markets by cosine similarity
        similarity_result = client.table("similarity_scores").select(
            "market_id_1, market_id_2, cosine_similarity"
        ).or_(
            f"market_id_1.eq.{source_token_ids},market_id_2.eq.{source_token_ids}"
        ).gte("cosine_similarity", min_similarity).order(
            "cosine_similarity", desc=True
        ).limit(limit * 2).execute()  # Fetch more for AI ranking
        
        if not similarity_result.data:
            logger.warning(f"[AI Similar] No cosine similarity matches found")
            # Fallback to fuzzy text search
            fuzzy_result = client.table("markets").select(
                "question, market_slug, clob_token_ids, tag_label"
            ).ilike("question", fuzzy_query).neq(
                "question", source_market.get("question")
            ).limit(limit).execute()
            
            similar_markets = [{
                **market,
                "match_type": "fuzzy_text",
                "cosine_similarity": 0.0
            } for market in fuzzy_result.data]
        else:
            # Extract related market IDs
            related_ids = []
            similarity_map = {}
            
            for row in similarity_result.data:
                related_id = row["market_id_2"] if row["market_id_1"] == source_token_ids else row["market_id_1"]
                if related_id and related_id != source_token_ids:
                    related_ids.append(related_id)
                    similarity_map[related_id] = row["cosine_similarity"]
            
            logger.info(f"[AI Similar] Found {len(related_ids)} similar markets")
            
            # Fetch market details
            if related_ids:
                markets_result = client.table("markets").select(
                    "question, market_slug, clob_token_ids, tag_label"
                ).in_("clob_token_ids", related_ids).execute()
                
                similar_markets = [{
                    **market,
                    "cosine_similarity": similarity_map.get(market.get("clob_token_ids"), 0.0),
                    "match_type": "cosine_similarity"
                } for market in markets_result.data]
                
                # Sort by similarity
                similar_markets.sort(key=lambda x: x.get("cosine_similarity", 0), reverse=True)
            else:
                similar_markets = []
        
        # Step 3: Optional AI ranking
        if use_ai_ranking and similar_markets:
            logger.info(f"[AI Similar] Using Gemini AI to rank {len(similar_markets)} results...")
            gemini = get_gemini_client()
            similar_markets = await gemini.rank_recommendations(
                primary_market=source_market.get("question"),
                candidate_markets=similar_markets,
                limit=limit
            )
            logger.info(f"[AI Similar] AI ranking complete")
        
        # Limit final results
        similar_markets = similar_markets[:limit]
        
        logger.info(f"[AI Similar] Returning {len(similar_markets)} results")
        logger.info(f"[AI Similar] ========================================")
        
        return JSONResponse(content={
            "source_market": source_market.get("question"),
            "count": len(similar_markets),
            "ai_ranked": use_ai_ranking,
            "similar_markets": similar_markets
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[AI Similar] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error finding similar markets: {str(e)}")


@app.get("/ai/analyze")
async def analyze_market_with_ai(
    market_title: str = Query(..., description="Market title to analyze")
):
    """
    Analyze a market using Gemini AI.
    
    Extracts:
    - Named entities (people, organizations, events)
    - Keywords and topics
    - Topic categories (Politics, Finance, etc.)
    
    Useful for understanding market context and finding correlations.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        gemini = get_gemini_client()
        analysis = gemini.extract_entities(market_title)
        
        logger.info(f"[AI Analyze] Analyzed: {market_title}")
        logger.info(f"[AI Analyze] Entities: {analysis.get('entities')}")
        logger.info(f"[AI Analyze] Topics: {analysis.get('topics')}")
        
        return JSONResponse(content={
            "market_title": market_title,
            "analysis": analysis
        })
    
    except Exception as e:
        logger.error(f"[AI Analyze] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing market: {str(e)}")


@app.get("/ai/semantic-similarity")
async def compute_semantic_similarity(
    title1: str = Query(..., description="First market title"),
    title2: str = Query(..., description="Second market title")
):
    """
    Compute semantic similarity between two markets using Gemini AI.
    
    Returns a score from 0 to 1:
    - 0.0 = Completely unrelated
    - 0.5 = Somewhat related
    - 1.0 = Highly related/correlated
    
    Uses AI to understand meaning, not just keyword matching.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        gemini = get_gemini_client()
        similarity = gemini.compute_semantic_similarity(title1, title2)
        
        logger.info(f"[AI Similarity] '{title1}' <-> '{title2}': {similarity:.3f}")
        
        return JSONResponse(content={
            "title1": title1,
            "title2": title2,
            "similarity_score": similarity,
            "interpretation": (
                "Highly related" if similarity > 0.7 else
                "Moderately related" if similarity > 0.4 else
                "Somewhat related" if similarity > 0.2 else
                "Unrelated"
            )
        })
    
    except Exception as e:
        logger.error(f"[AI Similarity] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error computing similarity: {str(e)}")