"""Polymarket Gamma API Client."""

import httpx
from typing import List, Dict, Any, Optional
import json

GAMMA_BASE = "https://gamma-api.polymarket.com"
TIMEOUT = 30

class GammaClient:
    def __init__(self):
        self.base_url = GAMMA_BASE
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
    
    async def get_tags(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch all tags from Gamma API"""
        response = await self.client.get(
            f"{self.base_url}/tags",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return []
        return data
    
    async def resolve_tag_ids(self, labels: List[str]) -> Dict[str, int]:
        """Resolve tag labels to tag IDs"""
        target_labels = {s.lower() for s in labels}
        resolved: Dict[str, int] = {}
        offset = 0
        
        while len(resolved) < len(target_labels):
            tags = await self.get_tags(limit=100, offset=offset)
            if not tags:
                break
            
            for tag in tags:
                label = str(tag.get("label", "")).strip().lower()
                if label in target_labels and label not in resolved:
                    resolved[label] = int(tag["id"])
            
            if len(resolved) >= len(target_labels):
                break
            
            offset += 100
            if offset > 1000:  # Safety limit
                break
        
        return resolved
    
    async def get_events_by_tag(
        self,
        tag_id: int,
        active: bool = True,
        closed: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Fetch events by tag ID"""
        params = {
            "tag_id": tag_id,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "limit": limit,
            "offset": offset,
        }
        response = await self.client.get(
            f"{self.base_url}/events",
            params=params
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return []
        return data
    
    async def get_market_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get market details by slug"""
        try:
            response = await self.client.get(
                f"{self.base_url}/markets",
                params={"slug": slug}
            )
            response.raise_for_status()
            markets = response.json()
            if isinstance(markets, list) and markets:
                return markets[0]
            return None
        except Exception as e:
            print(f"Error fetching market by slug {slug}: {e}")
            return None
    
    async def get_market_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract slug from URL and fetch market"""
        # Extract slug from URL like https://polymarket.com/event/...
        parts = url.rstrip('/').split('/')
        slug = parts[-1] if parts else None
        if not slug:
            return None
        return await self.get_market_by_slug(slug)
    
    def _maybe_json(self, value: Any) -> Any:
        """Parse JSON strings if needed"""
        if isinstance(value, str):
            s = value.strip()
            if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
                try:
                    return json.loads(s)
                except json.JSONDecodeError:
                    return value
        return value
    
    def extract_markets_from_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract markets from an event object"""
        markets = event.get("markets") or []
        if not isinstance(markets, list):
            return []
        
        result = []
        for market in markets:
            outcomes = self._maybe_json(market.get("outcomes"))
            clob_token_ids = self._maybe_json(market.get("clobTokenIds"))
            
            result.append({
                "id": market.get("id"),
                "slug": market.get("slug"),
                "title": market.get("question") or market.get("title") or market.get("name"),
                "outcomes": outcomes,
                "clob_token_ids": clob_token_ids,
                "active": market.get("active", False),
                "closed": market.get("closed", False),
                "event_id": event.get("id"),
                "event_slug": event.get("slug"),
                "event_title": event.get("title") or event.get("name"),
            })
        
        return result
    
    async def discover_markets_by_topics(
        self,
        tag_ids: List[int],
        limit_per_topic: int = 50
    ) -> List[Dict[str, Any]]:
        """Discover markets for given topic tag IDs"""
        all_markets = []
        
        for tag_id in tag_ids:
            events = await self.get_events_by_tag(tag_id, active=True, limit=limit_per_topic)
            for event in events:
                markets = self.extract_markets_from_event(event)
                for market in markets:
                    if market.get("active") and not market.get("closed"):
                        market["topic_tag_id"] = tag_id
                        all_markets.append(market)
        
        return all_markets
    
    async def close(self):
        await self.client.aclose()
