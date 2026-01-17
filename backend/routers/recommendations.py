from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from clients.gamma_client import GammaClient
from clients.gemini_client import GeminiClient
from clients.clob_client import ClobClient
from services.cache import CacheService
from services.recommendation_engine import RecommendationEngine

router = APIRouter()

# Initialize clients (singleton pattern)
gamma_client = GammaClient()
gemini_client = GeminiClient()
clob_client = ClobClient()
cache_service = CacheService()
recommendation_engine = RecommendationEngine(
    gamma_client,
    gemini_client,
    clob_client,
    cache_service
)

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
