from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional

<<<<<<< HEAD
from polymarket.get_markets_data import ui
from polymarket.get_similar_markets import get_similar_by_event_title
from polymarket.get_related_traded import get_related_traded, get_related_traded_by_market_id, get_related_traded_by_event_title
from services.trending import TrendingService
from services.polymarket_api import PolymarketAPIService
=======
from Polymarket_API.get_markets_data import ui
from Polymarket_API.get_similar_markets import get_similar_by_event_title
from Polymarket_API.news import fetch_news

>>>>>>> 01df126405e4250096e12c73466eaf2e39b7dce5

app = FastAPI(
    title="NexHacks Polymarket Correlation Tool",
    version="1.0.0",
    description="API for Polymarket correlation, trending, and parlay suggestions"
)

# Initialize services
trending_service = TrendingService()
polymarket_api = PolymarketAPIService()


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "NexHacks Polymarket API",
        "version": "1.0.0",
        "endpoints": {
            "trending": "/markets/trending",
            "ui": "/ui"
        }
    }


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
        markets = trending_service.get_trending_markets(
            category=category,
            limit=limit,
            min_score=min_score
        )
        
        return {
            "count": len(markets),
            "markets": markets
        }
    
    except Exception as e:
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
        updated = polymarket_api.fetch_and_update_metrics(limit=limit)
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
def get_similar(
    event_title: str = Query(..., description="Exact market question title")
):
    """Get similar markets by text similarity (cosine similarity)"""
    try:
        data = get_similar_by_event_title(event_title)
        if not data:
            raise HTTPException(status_code=404, detail="Event not found")
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
<<<<<<< HEAD


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
=======
    
@app.get("/news")
def get_news(
    question: str = Query(..., description="Event or market question")
):
    try:
        data = fetch_news(question.strip())
        if not data:
            raise HTTPException(status_code=404, detail="No articles found")
>>>>>>> 01df126405e4250096e12c73466eaf2e39b7dce5
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))