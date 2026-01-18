from typing import List, Dict, Any, Optional
from datetime import datetime
from clients.gamma_client import GammaClient
from clients.gemini_client import GeminiClient
from clients.clob_client import ClobClient
from services.scoring import ScoringService
from services.correlation import CorrelationService
from services.cache import CacheService

LOCKED_TOPICS = ["Finance", "Politics", "Technology", "Elections", "Economy"]

class RecommendationEngine:
    def __init__(
        self,
        gamma_client: GammaClient,
        gemini_client: GeminiClient,
        clob_client: ClobClient,
        cache_service: CacheService
    ):
        self.gamma = gamma_client
        self.gemini = gemini_client
        self.clob = clob_client
        self.cache = cache_service
        self.scoring = ScoringService(gemini_client)
        self.correlation = CorrelationService(clob_client)
        self.topic_tag_ids: Dict[str, int] = {}
    
    async def initialize_topics(self):
        """Resolve locked topic tag IDs"""
        topic_labels = [t.lower() for t in LOCKED_TOPICS]
        self.topic_tag_ids = await self.gamma.resolve_tag_ids(topic_labels)
    
    async def resolve_primary_market(self, url: str) -> Optional[Dict[str, Any]]:
        """Resolve primary market from URL"""
        # Check cache first
        cache_key = url.split('/')[-1]
        cached = await self.cache.get_market_metadata(cache_key)
        if cached:
            return cached
        
        market = await self.gamma.get_market_by_url(url)
        if market:
            # Extract topics from market tags
            topics = []
            # Market tags would be in market.get("tags") or similar
            # For now, we'll discover topics from events
            
            result = {
                "market_id": market.get("id"),
                "title": market.get("title") or market.get("question"),
                "slug": market.get("slug"),
                "token_ids": self._extract_token_ids(market),
                "topics": topics,
            }
            
            await self.cache.set_market_metadata(cache_key, result)
            return result
        
        return None
    
    def _extract_token_ids(self, market: Dict[str, Any]) -> List[str]:
        """Extract CLOB token IDs from market"""
        clob_token_ids = market.get("clobTokenIds") or []
        if isinstance(clob_token_ids, str):
            import json
            try:
                clob_token_ids = json.loads(clob_token_ids)
            except:
                clob_token_ids = []
        if not isinstance(clob_token_ids, list):
            return []
        return [str(tid) for tid in clob_token_ids if tid]
    
    async def discover_candidate_markets(
        self,
        primary_market: Dict[str, Any],
        local_profile: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Discover candidate markets from locked topics"""
        if not self.topic_tag_ids:
            await self.initialize_topics()
        
        tag_ids = list(self.topic_tag_ids.values())
        candidates = await self.gamma.discover_markets_by_topics(tag_ids, limit_per_topic=20)
        
        # Filter out primary market
        primary_id = primary_market.get("market_id")
        candidates = [c for c in candidates if c.get("id") != primary_id]
        
        return candidates[:limit]
    
    async def build_five_market_set(
        self,
        primary_market: Dict[str, Any],
        local_profile: Dict[str, Any],
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build 5-market set: primary + 2 from history + 2 top amplify"""
        five_set = [primary_market]
        
        # Markets 2-3: Most relevant from local history
        recent_interactions = local_profile.get("recent_interactions", [])[:20]
        history_markets = []
        
        for interaction in recent_interactions:
            interaction_url = interaction.get("marketUrl", "")
            if interaction_url:
                market = await self.gamma.get_market_by_url(interaction_url)
                if market and market.get("id") != primary_market.get("market_id"):
                    history_markets.append(market)
        
        # Score and select top 2 from history
        primary_title = primary_market.get("title", "")
        scored_history = []
        
        for market in history_markets[:10]:  # Limit to avoid too many API calls
            title = market.get("title") or market.get("question", "")
            score = self.gemini.compute_semantic_similarity(primary_title, title)
            scored_history.append((score, market))
        
        scored_history.sort(key=lambda x: x[0], reverse=True)
        for _, market in scored_history[:2]:
            if len(five_set) < 3:
                five_set.append({
                    "id": market.get("id"),
                    "title": market.get("title") or market.get("question"),
                    "token_id": self._extract_token_ids(market)[0] if self._extract_token_ids(market) else "",
                })
        
        # Markets 4-5: Top amplify candidates (will be computed in generate_recommendations)
        # Placeholder - will be filled by top amplify markets
        
        return five_set
    
    async def generate_recommendations(
        self,
        primary: Dict[str, Any],
        local_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate amplify and hedge recommendations"""
        # Resolve primary market
        primary_resolved = await self.resolve_primary_market(primary["url"])
        if not primary_resolved:
            raise ValueError("Could not resolve primary market")
        
        # Discover candidates
        candidates = await self.discover_candidate_markets(primary_resolved, local_profile)
        
        # Extract entities from primary
        primary_title = primary_resolved.get("title", "")
        primary_entities_data = self.gemini.extract_entities(primary_title)
        primary_entities = primary_entities_data.get("entities", [])
        
        # Score all candidates
        scored_amplify = []
        scored_hedge = []
        
        primary_token_ids = primary_resolved.get("token_ids", [])
        primary_token_id = primary_token_ids[0] if primary_token_ids else None
        
        for candidate in candidates[:50]:  # Limit for performance
            candidate_title = candidate.get("title", "")
            candidate_id = candidate.get("id")
            candidate_token_ids = self._extract_token_ids(candidate)
            candidate_token_id = candidate_token_ids[0] if candidate_token_ids else None
            
            # Extract entities
            candidate_entities_data = self.gemini.extract_entities(candidate_title)
            candidate_entities = candidate_entities_data.get("entities", [])
            
            # Compute similarity score
            similarity = self.scoring.compute_similarity_score(
                primary_title,
                candidate_title,
                primary_entities,
                candidate_entities
            )
            
            # Get correlation if available
            correlation = None
            if primary_token_id and candidate_token_id:
                correlation = await self.correlation.get_pair_correlation(
                    primary_token_id,
                    candidate_token_id,
                    window_days=30
                )
            
            # Amplify score
            amplify_score = similarity
            if local_profile.get("recent_interactions"):
                # Apply recency weighting
                for interaction in local_profile["recent_interactions"][:5]:
                    amplify_score = self.scoring.apply_recency_weight(
                        amplify_score,
                        interaction,
                        datetime.utcnow()
                    )
            
            # Hedge score
            hedge_data = self.scoring.compute_hedge_score(
                primary_title,
                candidate_title,
                primary.get("side", "YES"),
                correlation
            )
            
            # Get topic label
            topic_tag_id = candidate.get("topic_tag_id")
            topic_label = None
            for label, tag_id in self.topic_tag_ids.items():
                if tag_id == topic_tag_id:
                    topic_label = label.capitalize()
                    break
            
            candidate_url = f"https://polymarket.com/event/{candidate.get('slug', candidate_id)}"
            
            scored_amplify.append({
                "id": candidate_id,
                "title": candidate_title,
                "url": candidate_url,
                "topic": topic_label or "Unknown",
                "score": amplify_score,
                "reason": f"Similar to primary market (similarity: {similarity:.2f})",
            })
            
            scored_hedge.append({
                "id": candidate_id,
                "title": candidate_title,
                "url": candidate_url,
                "topic": topic_label or "Unknown",
                "score": hedge_data["score"],
                "reason": f"Hedging potential ({hedge_data['type']})",
                "hedge_type": hedge_data["type"],
            })
        
        # Sort and take top 5
        scored_amplify.sort(key=lambda x: x["score"], reverse=True)
        scored_hedge.sort(key=lambda x: x["score"], reverse=True)
        
        amplify = scored_amplify[:5]
        hedge = scored_hedge[:5]
        
        # Build 5-market set
        five_set = await self.build_five_market_set(primary_resolved, local_profile, candidates)
        
        # Fill markets 4-5 from top amplify
        for rec in amplify[:2]:
            if len(five_set) < 5:
                token_ids = self._extract_token_ids(
                    next((c for c in candidates if c.get("id") == rec["id"]), {})
                )
                five_set.append({
                    "id": rec["id"],
                    "title": rec["title"],
                    "token_id": token_ids[0] if token_ids else "",
                })
        
        # Compute correlation matrix for 5-market set
        token_ids = [m.get("token_id") for m in five_set if m.get("token_id")]
        corr_matrix = None
        corr_coverage = 0.0
        window_used = "30d"
        
        if len(token_ids) >= 2:
            matrix, coverage = await self.correlation.compute_correlation_matrix(
                token_ids,
                window_days=30
            )
            if matrix is not None:
                corr_matrix = matrix.tolist()
                corr_coverage = coverage
            else:
                # Try 7d window
                matrix, coverage = await self.correlation.compute_correlation_matrix(
                    token_ids,
                    window_days=7
                )
                if matrix is not None:
                    corr_matrix = matrix.tolist()
                    corr_coverage = coverage
                    window_used = "7d"
        
        return {
            "primary_resolved": primary_resolved,
            "amplify": amplify,
            "hedge": hedge,
            "five_set": five_set,
            "corr": {
                "window_used": window_used,
                "matrix": corr_matrix,
                "coverage": corr_coverage,
            } if corr_matrix else None,
        }
