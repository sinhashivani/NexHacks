import React from 'react';
import type { MarketRecommendation } from '../types';

interface MarketListProps {
  markets: MarketRecommendation[];
  onAddLeg: (market: { id: string; title: string; url: string; topic?: string }) => void;
}

export const MarketList: React.FC<MarketListProps> = ({ markets, onAddLeg }) => {
  if (markets.length === 0) {
    return <div className="market-list-empty">No recommendations available</div>;
  }
  
  return (
    <div className="market-list">
      {markets.map((market) => (
        <div key={market.id} className="market-item">
          <div className="market-header">
            <h4 className="market-title">{market.title}</h4>
            {market.topic && <span className="market-topic">{market.topic}</span>}
          </div>
          <div className="market-score">
            Score: <span className="score-value">{(market.score * 100).toFixed(0)}%</span>
          </div>
          <div className="market-reason">{market.reason}</div>
          {market.hedge_type && (
            <div className="market-hedge-type">Type: {market.hedge_type}</div>
          )}
          <div className="market-actions">
            <button
              className="btn-add-leg"
              onClick={() => onAddLeg({
                id: market.id,
                title: market.title,
                url: market.url,
                topic: market.topic,
              })}
            >
              Add Leg
            </button>
            <button
              className="btn-open-market"
              onClick={() => window.open(market.url, '_blank')}
            >
              Open Market
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
