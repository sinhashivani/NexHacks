import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from clients.clob_client import ClobClient

class CorrelationService:
    def __init__(self, clob_client: ClobClient):
        self.clob = clob_client
    
    async def compute_returns(
        self,
        token_id: str,
        days: int = 30
    ) -> Optional[pd.Series]:
        """Fetch price history and compute returns"""
        history = await self.clob.get_price_history_window(token_id, days=days)
        if not history or len(history) < 2:
            return None
        
        # Parse price history (adjust based on actual CLOB API response format)
        prices = []
        timestamps = []
        
        for entry in history:
            # Adjust field names based on actual API response
            price = entry.get("price") or entry.get("lastPrice") or entry.get("midPrice")
            timestamp = entry.get("timestamp") or entry.get("time")
            
            if price is not None and timestamp is not None:
                prices.append(float(price))
                timestamps.append(timestamp)
        
        if len(prices) < 2:
            return None
        
        # Create DataFrame and compute returns
        df = pd.DataFrame({"price": prices, "timestamp": timestamps})
        df = df.sort_values("timestamp")
        df["returns"] = df["price"].pct_change()
        
        return df["returns"].dropna()
    
    async def compute_correlation_matrix(
        self,
        token_ids: List[str],
        window_days: int = 30
    ) -> Tuple[Optional[np.ndarray], float]:
        """
        Compute correlation matrix for a set of tokens.
        Returns (matrix, coverage) where coverage is the fraction of pairs with data.
        """
        if len(token_ids) < 2:
            return None, 0.0
        
        # Fetch returns for all tokens
        returns_data: Dict[str, pd.Series] = {}
        for token_id in token_ids:
            returns = await self.compute_returns(token_id, days=window_days)
            if returns is not None and len(returns) > 5:  # Minimum data points
                returns_data[token_id] = returns
        
        if len(returns_data) < 2:
            return None, 0.0
        
        # Align time series
        df = pd.DataFrame(returns_data)
        df = df.dropna()  # Remove rows with missing data
        
        if len(df) < 5:
            return None, 0.0
        
        # Compute correlation matrix
        corr_matrix = df.corr().values
        
        # Compute coverage (fraction of pairs with valid correlation)
        n_pairs = len(token_ids) * (len(token_ids) - 1) / 2
        valid_pairs = 0
        for i in range(len(token_ids)):
            for j in range(i + 1, len(token_ids)):
                if token_ids[i] in returns_data and token_ids[j] in returns_data:
                    valid_pairs += 1
        
        coverage = valid_pairs / n_pairs if n_pairs > 0 else 0.0
        
        return corr_matrix, coverage
    
    async def get_pair_correlation(
        self,
        token_id1: str,
        token_id2: str,
        window_days: int = 30
    ) -> Optional[float]:
        """Get correlation between two tokens"""
        returns1 = await self.compute_returns(token_id1, days=window_days)
        returns2 = await self.compute_returns(token_id2, days=window_days)
        
        if returns1 is None or returns2 is None:
            return None
        
        # Align series
        aligned = pd.DataFrame({"r1": returns1, "r2": returns2}).dropna()
        
        if len(aligned) < 5:
            return None
        
        correlation = aligned["r1"].corr(aligned["r2"])
        return correlation if not np.isnan(correlation) else None
