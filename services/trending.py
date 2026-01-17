"""
Trending Markets Service
Calculates trending scores and ranks markets by popularity
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database.supabase_connection import SupabaseConnection


class TrendingService:
    def __init__(self):
        self.conn = SupabaseConnection()
        self.client = self.conn.get_client()
    
    def calculate_trending_score(
        self,
        open_interest: float = 0,
        volume_24h: float = 0,
        liquidity: float = 0,
        w1: float = 0.5,  # Weight for open interest
        w2: float = 0.3,  # Weight for volume
        w3: float = 0.2   # Weight for liquidity
    ) -> float:
        """
        Calculate trending score using weighted formula
        
        Args:
            open_interest: Current open interest
            volume_24h: 24-hour volume
            liquidity: Market liquidity
            w1, w2, w3: Weights for each metric (should sum to 1.0)
        
        Returns:
            Trending score (0-1, higher is more trending)
        """
        # Normalize values (simple min-max normalization)
        # For now, use log scaling to handle wide ranges
        import math
        
        # Use log scaling to prevent outliers from dominating
        norm_oi = math.log1p(open_interest) if open_interest > 0 else 0
        norm_vol = math.log1p(volume_24h) if volume_24h > 0 else 0
        norm_liq = math.log1p(liquidity) if liquidity > 0 else 0
        
        # Find max values for normalization (or use fixed thresholds)
        # For simplicity, use fixed normalization factors
        max_oi = 1000000  # 1M open interest
        max_vol = 100000  # 100K volume
        max_liq = 50000   # 50K liquidity
        
        normalized_oi = min(norm_oi / math.log1p(max_oi), 1.0)
        normalized_vol = min(norm_vol / math.log1p(max_vol), 1.0)
        normalized_liq = min(norm_liq / math.log1p(max_liq), 1.0)
        
        # Calculate weighted score
        score = (w1 * normalized_oi + w2 * normalized_vol + w3 * normalized_liq)
        
        # Ensure score is between 0 and 1
        return min(max(score, 0.0), 1.0)
    
    def get_trending_markets(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        min_score: float = 0.0
    ) -> List[Dict]:
        """
        Get trending markets ranked by popularity
        
        Args:
            category: Optional category filter (e.g., 'politics', 'sports', 'tech')
            limit: Maximum number of results
            min_score: Minimum trending score threshold
        
        Returns:
            List of trending markets with scores
        """
        try:
            # Build query for markets
            query = self.client.table("markets").select(
                "market_id, market_slug, question, tag_label, tag_id, active, closed"
            )
            
            # Filter active markets only
            query = query.eq("active", True).eq("closed", False)
            
            # Filter by category if provided
            if category:
                query = query.eq("tag_label", category.lower())
            
            # Get markets
            markets_response = query.execute()
            markets = markets_response.data if hasattr(markets_response, 'data') else []
            
            if not markets:
                return []
            
            # Get market IDs
            market_ids = [m["market_id"] for m in markets]
            
            # Get metrics for these markets
            metrics_query = self.client.table("market_metrics").select(
                "market_id, last_price, open_interest, volume_24h, liquidity"
            ).in_("market_id", market_ids)
            
            metrics_response = metrics_query.execute()
            metrics_data = metrics_response.data if hasattr(metrics_response, 'data') else []
            
            # Create metrics lookup
            metrics_dict = {m["market_id"]: m for m in metrics_data}
            
            # Calculate trending scores and combine
            results = []
            for market in markets:
                market_id = market["market_id"]
                metrics = metrics_dict.get(market_id, {})
                
                # Get metrics with defaults
                open_interest = float(metrics.get("open_interest", 0) or 0)
                volume_24h = float(metrics.get("volume_24h", 0) or 0)
                liquidity = float(metrics.get("liquidity", 0) or 0)
                
                # Calculate trending score
                trending_score = self.calculate_trending_score(
                    open_interest=open_interest,
                    volume_24h=volume_24h,
                    liquidity=liquidity
                )
                
                # Skip if below minimum score
                if trending_score < min_score:
                    continue
                
                results.append({
                    "market_id": market_id,
                    "market_slug": market.get("market_slug"),
                    "question": market.get("question"),
                    "canonical_category": market.get("tag_label"),
                    "trending_score": round(trending_score, 4),
                    "open_interest": open_interest,
                    "volume_24h": volume_24h,
                    "liquidity": liquidity,
                    "last_price": metrics.get("last_price")
                })
            
            # Sort by trending score (descending)
            results.sort(key=lambda x: x["trending_score"], reverse=True)
            
            # Return top N
            return results[:limit]
        
        except Exception as e:
            print(f"Error getting trending markets: {e}")
            return []
    
    def update_market_metrics(self, market_id: str, metrics: Dict) -> bool:
        """
        Update or insert market metrics
        
        Args:
            market_id: Market ID
            metrics: Dict with last_price, open_interest, volume_24h, liquidity
        
        Returns:
            True if successful
        """
        try:
            data = {
                "market_id": market_id,
                "last_price": metrics.get("last_price"),
                "open_interest": metrics.get("open_interest", 0),
                "volume_24h": metrics.get("volume_24h", 0),
                "liquidity": metrics.get("liquidity", 0),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert metrics
            self.client.table("market_metrics").upsert(data).execute()
            return True
        
        except Exception as e:
            print(f"Error updating market metrics: {e}")
            return False
