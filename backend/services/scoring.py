from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from clients.gemini_client import GeminiClient

class ScoringService:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini = gemini_client
    
    def compute_similarity_score(
        self,
        primary_title: str,
        candidate_title: str,
        primary_entities: List[str],
        candidate_entities: List[str]
    ) -> float:
        """Compute similarity score between primary and candidate market"""
        # Semantic similarity (0.6 weight) - Gemini client is synchronous
        semantic_score = self.gemini.compute_semantic_similarity(
            primary_title,
            candidate_title
        )
        
        # Entity overlap (0.4 weight)
        entity_overlap = 0.0
        if primary_entities and candidate_entities:
            primary_set = set(primary_entities)
            candidate_set = set(candidate_entities)
            if primary_set or candidate_set:
                intersection = primary_set.intersection(candidate_set)
                union = primary_set.union(candidate_set)
                entity_overlap = len(intersection) / len(union) if union else 0.0
        
        return 0.6 * semantic_score + 0.4 * entity_overlap
    
    def compute_hedge_score(
        self,
        primary_title: str,
        candidate_title: str,
        primary_side: str,
        correlation: Optional[float] = None
    ) -> Dict[str, Any]:
        """Compute hedging score and type"""
        # Negative correlation indicates hedging potential
        if correlation is not None:
            hedge_score = abs(correlation) if correlation < 0 else (1 - correlation) / 2
            hedge_type = "inverse" if correlation < -0.3 else "diversification"
        else:
            # Fallback: semantic dissimilarity - Gemini client is synchronous
            similarity = self.gemini.compute_semantic_similarity(primary_title, candidate_title)
            hedge_score = 1 - similarity
            hedge_type = "diversification"
        
        return {
            "score": hedge_score,
            "type": hedge_type,
            "correlation": correlation,
        }
    
    def apply_recency_weight(
        self,
        base_score: float,
        interaction: Dict[str, Any],
        now: datetime
    ) -> float:
        """Apply recency weighting to score based on interaction timestamp"""
        timestamp = interaction.get("timestamp", 0)
        age_days = (now.timestamp() * 1000 - timestamp) / (1000 * 60 * 60 * 24)
        decay_days = 30
        weight = max(0, 1 - age_days / decay_days)
        return base_score * (1 + weight * 0.2)  # Boost by up to 20%
