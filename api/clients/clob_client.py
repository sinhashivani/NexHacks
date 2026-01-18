"""Polymarket CLOB API Client for live price data."""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

CLOB_BASE = "https://clob.polymarket.com"
TIMEOUT = 30

class ClobClient:
    def __init__(self):
        self.base_url = CLOB_BASE
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
    
    async def get_price_history(
        self,
        token_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch price history for a token"""
        params = {"token_id": token_id}
        
        if start_time:
            params["start_time"] = int(start_time.timestamp())
        if end_time:
            params["end_time"] = int(end_time.timestamp())
        
        try:
            response = await self.client.get(
                f"{self.base_url}/prices-history",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"Error fetching price history for {token_id}: {e}")
            return []
    
    async def get_price_history_window(
        self,
        token_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price history for a specific time window"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        return await self.get_price_history(token_id, start_time, end_time)
    
    async def get_current_price(self, token_id: str) -> Optional[float]:
        """Get current price for a token"""
        try:
            history = await self.get_price_history_window(token_id, days=1)
            if history:
                # Get the most recent price
                latest = max(history, key=lambda x: x.get("timestamp", 0))
                price = latest.get("price") or latest.get("lastPrice") or latest.get("midPrice")
                return float(price) if price is not None else None
            return None
        except Exception as e:
            print(f"Error fetching current price for {token_id}: {e}")
            return None
    
    async def close(self):
        await self.client.aclose()
