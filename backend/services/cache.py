from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from database import get_database

class CacheService:
    def __init__(self):
        self.db = get_database()
        # If database is None, we're in mock mode
        self.cache_collection = self.db["cache"] if self.db else None
        self.local_cache: Dict[str, Dict[str, Any]] = {}  # In-memory fallback
    
    async def get_market_metadata(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get cached market metadata"""
        # Try in-memory cache first (always available)
        if market_id in self.local_cache:
            cached_item = self.local_cache[market_id]
            if cached_item.get("expires_at", 0) > datetime.utcnow().timestamp():
                return cached_item.get("data")
        
        # Try database if available
        if self.cache_collection:
            doc = await self.cache_collection.find_one({
                "type": "market_metadata",
                "market_id": market_id,
            })
            
            if doc and doc.get("expires_at", 0) > datetime.utcnow().timestamp():
                return doc.get("data")
        
        return None
    
    async def set_market_metadata(
        self,
        market_id: str,
        data: Dict[str, Any],
        ttl_hours: int = 24
    ):
        """Cache market metadata"""
        expires_at = (datetime.utcnow() + timedelta(hours=ttl_hours)).timestamp()
        
        # Store in local cache (always available)
        self.local_cache[market_id] = {
            "data": data,
            "expires_at": expires_at
        }
        
        # Store in database if available
        if self.cache_collection:
            await self.cache_collection.update_one(
                {
                    "type": "market_metadata",
                    "market_id": market_id,
                },
                {
                    "$set": {
                        "data": data,
                        "expires_at": expires_at,
                        "updated_at": datetime.utcnow().timestamp(),
                    }
                },
                upsert=True
            )
    
    async def get_price_history(
        self,
        token_id: str,
        window_days: int
    ) -> Optional[Dict[str, Any]]:
        """Get cached price history"""
        cache_key = f"price_history_{token_id}_{window_days}"
        
        # Try in-memory cache first
        if cache_key in self.local_cache:
            cached_item = self.local_cache[cache_key]
            if cached_item.get("expires_at", 0) > datetime.utcnow().timestamp():
                return cached_item.get("data")
        
        # Try database if available
        if self.cache_collection:
            doc = await self.cache_collection.find_one({
                "type": "price_history",
                "cache_key": cache_key,
            })
            
            if doc and doc.get("expires_at", 0) > datetime.utcnow().timestamp():
                return doc.get("data")
        
        return None
    
    async def set_price_history(
        self,
        token_id: str,
        window_days: int,
        data: Dict[str, Any],
        ttl_hours: int = 1
    ):
        """Cache price history"""
        cache_key = f"price_history_{token_id}_{window_days}"
        expires_at = (datetime.utcnow() + timedelta(hours=ttl_hours)).timestamp()
        
        # Store in local cache (always available)
        self.local_cache[cache_key] = {
            "data": data,
            "expires_at": expires_at
        }
        
        # Store in database if available
        if self.cache_collection:
            await self.cache_collection.update_one(
                {
                    "type": "price_history",
                    "cache_key": cache_key,
                },
                {
                    "$set": {
                        "data": data,
                        "expires_at": expires_at,
                        "updated_at": datetime.utcnow().timestamp(),
                    }
                },
                upsert=True
            )
    
    async def cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.utcnow().timestamp()
        await self.cache_collection.delete_many({
            "expires_at": {"$lt": now}
        })
