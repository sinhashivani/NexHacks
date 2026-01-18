from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from clients.gamma_client import GammaClient
from clients.gemini_client import GeminiClient
from clients.clob_client import ClobClient
from services.cache import CacheService
from services.recommendation_engine import RecommendationEngine

router = APIRouter()

# Initialize clients (singleton pattern) - lazy loaded to avoid startup errors
_gamma_client = None
_gemini_client = None
_clob_client = None
_cache_service = None
_recommendation_engine = None

def get_clients():
    global _gamma_client, _gemini_client, _clob_client, _cache_service, _recommendation_engine
    if _gamma_client is None:
        try:
            _gamma_client = GammaClient()
            _gemini_client = GeminiClient()
            _clob_client = ClobClient()
            _cache_service = CacheService()
            _recommendation_engine = RecommendationEngine(
                _gamma_client,
                _gemini_client,
                _clob_client,
                _cache_service,
            )
        except Exception as e:
            print(f"⚠️  Error initializing services: {e}")
            raise
    return _gamma_client, _gemini_client, _clob_client, _cache_service, _recommendation_engine

gamma_client = None
gemini_client = None
clob_client = None
cache_service = None
recommendation_engine = None

class MarketInteraction(BaseModel):
    timestamp: int
    marketUrl: str
    side: Optional[str] = None
    amount: Optional[float] = None
    interaction_type: str  # 'hover_open' or 'ticket_open'

class LocalProfile(BaseModel):
    recent_interactions: List[MarketInteraction]
    topic_counts: Dict[str, float]
    entity_counts: Dict[str, float]

class PrimaryMarket(BaseModel):
    url: str
    side: Optional[str] = None
    amount: Optional[float] = None
    trigger_type: str  # 'hover' or 'ticket_open'

class RecommendationRequest(BaseModel):
    primary: PrimaryMarket
    local_profile: LocalProfile

@router.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Generate amplify and hedge recommendations"""
    try:
        # Initialize clients on first use
        global recommendation_engine
        if recommendation_engine is None:
            _, _, _, _, recommendation_engine = get_clients()
        
        # Convert request to dict for engine
        primary_dict = request.primary.dict()
        local_profile_dict = request.local_profile.dict()
        
        result = await recommendation_engine.generate_recommendations(
            primary_dict,
            local_profile_dict
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
