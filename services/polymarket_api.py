"""
Polymarket API Service
Fetches live market data from Polymarket APIs
"""

from typing import List, Dict, Optional
import requests
import json
from polymarket.get_markets_data import GAMMA, CLOB, _get, _to_list, mid


class PolymarketAPIService:
    """Service for fetching data from Polymarket APIs"""
    
    def __init__(self):
        self.gamma_base = GAMMA
        self.clob_base = CLOB
        self.timeout = 15
    
    def get_active_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        tag_id: Optional[int] = None,
        active: bool = True,
        closed: bool = False
    ) -> List[Dict]:
        """
        Fetch active markets from Polymarket Gamma API
        
        Args:
            limit: Number of markets to fetch
            offset: Pagination offset
            tag_id: Optional tag filter
            active: Filter active markets
            closed: Filter closed markets
        
        Returns:
            List of market dictionaries
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
                "active": str(active).lower(),
                "closed": str(closed).lower()
            }
            
            if tag_id:
                params["tag_id"] = tag_id
            
            response = _get(f"{self.gamma_base}/markets", params)
            
            if not isinstance(response, list):
                return []
            
            return response
        
        except Exception as e:
            print(f"Error fetching active markets: {e}")
            return []
    
    def get_market_by_id(self, market_id: str) -> Optional[Dict]:
        """
        Get market by ID
        
        Args:
            market_id: Market ID
        
        Returns:
            Market dictionary or None
        """
        try:
            markets = self.get_active_markets(limit=1)
            # Search for market with matching ID
            for market in markets:
                if str(market.get("id")) == str(market_id):
                    return market
            return None
        except Exception as e:
            print(f"Error fetching market by ID: {e}")
            return None
    
    def get_market_metrics(self, market: Dict) -> Dict:
        """
        Extract metrics from a market object
        
        Args:
            market: Market dictionary from Gamma API
        
        Returns:
            Metrics dictionary with price, volume, etc.
        """
        try:
            # Get token IDs
            token_ids = _to_list(market.get("clobTokenIds"))
            
            # Get prices for tokens
            prices = []
            for token_id in token_ids:
                price = mid(token_id)
                if price:
                    try:
                        prices.append(float(price))
                    except (ValueError, TypeError):
                        pass
            
            # Calculate metrics
            last_price = prices[0] if prices else None
            
            # Get volume and open interest from market data if available
            volume_24h = float(market.get("volume", 0) or 0)
            open_interest = float(market.get("openInterest", 0) or market.get("liquidity", 0) or 0)
            liquidity = float(market.get("liquidity", 0) or market.get("depth", 0) or 0)
            
            return {
                "last_price": last_price,
                "open_interest": open_interest,
                "volume_24h": volume_24h,
                "liquidity": liquidity
            }
        
        except Exception as e:
            print(f"Error extracting market metrics: {e}")
            return {
                "last_price": None,
                "open_interest": 0,
                "volume_24h": 0,
                "liquidity": 0
            }
    
    def fetch_and_update_metrics(self, limit: int = 100) -> int:
        """
        Fetch markets from Polymarket and update metrics in database
        
        Args:
            limit: Number of markets to process
        
        Returns:
            Number of markets updated
        """
        from services.trending import TrendingService
        
        trending_service = TrendingService()
        markets = self.get_active_markets(limit=limit)
        
        updated = 0
        for market in markets:
            market_id = str(market.get("id"))
            if not market_id:
                continue
            
            # Get metrics
            metrics = self.get_market_metrics(market)
            
            # Update in database
            if trending_service.update_market_metrics(market_id, metrics):
                updated += 1
        
        return updated
