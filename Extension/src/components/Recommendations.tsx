import React, { useState, useEffect } from 'react';
import { generateAmplifyRecommendations, generateHedgeRecommendations } from '../utils/recommendations';
import { getBasket, saveBasket } from '../utils/storage';
import type { MarketRecommendation, BasketLeg } from '../types';
import './Recommendations.css';

interface RecommendationsProps {
  currentUrl: string;
}

export const Recommendations: React.FC<RecommendationsProps> = ({ currentUrl }) => {
  const [activeTab, setActiveTab] = useState<'amplify' | 'hedge'>('amplify');
  const [amplify, setAmplify] = useState<MarketRecommendation[]>([]);
  const [hedge, setHedge] = useState<MarketRecommendation[]>([]);
  const [basket, setBasket] = useState<BasketLeg[]>([]);

  useEffect(() => {
    // Generate recommendations on mount
    setAmplify(generateAmplifyRecommendations(currentUrl));
    setHedge(generateHedgeRecommendations(currentUrl));
    
    // Load basket
    loadBasket();
  }, [currentUrl]);

  async function loadBasket() {
    const saved = await getBasket();
    setBasket(saved);
  }

  async function handleAddToBasket(market: MarketRecommendation) {
    const newLeg: BasketLeg = {
      id: market.id,
      title: market.title,
      url: market.url,
      category: market.category,
      visited: false,
    };
    
    const updated = [...basket, newLeg];
    setBasket(updated);
    await saveBasket(updated);
  }

  async function handleRemoveLeg(id: string) {
    const updated = basket.filter(leg => leg.id !== id);
    setBasket(updated);
    await saveBasket(updated);
  }

  function handleOpenNextUnvisited() {
    const unvisited = basket.find(leg => !leg.visited);
    if (unvisited) {
      window.open(unvisited.url, '_blank');
      const updated = basket.map(leg =>
        leg.id === unvisited.id ? { ...leg, visited: true } : leg
      );
      setBasket(updated);
      saveBasket(updated);
    }
  }

  const recommendations = activeTab === 'amplify' ? amplify : hedge;

  return (
    <div className="recommendations-section">
      <div className="recommendations-tabs">
        <button
          className={`tab-button ${activeTab === 'amplify' ? 'active' : ''}`}
          onClick={() => setActiveTab('amplify')}
        >
          Amplify
        </button>
        <button
          className={`tab-button ${activeTab === 'hedge' ? 'active' : ''}`}
          onClick={() => setActiveTab('hedge')}
        >
          Hedge
        </button>
      </div>

      <div className="recommendations-list">
        {recommendations.map((market) => (
          <div key={market.id} className="recommendation-item">
            <div className="recommendation-header">
              <h4 className="recommendation-title">{market.title}</h4>
              <span className="recommendation-category">{market.category}</span>
            </div>
            <div className="recommendation-score">
              Score: <span className="score-value">{(market.score * 100).toFixed(0)}%</span>
            </div>
            <div className="recommendation-reason">{market.reason}</div>
            <div className="recommendation-actions">
              <button
                className="btn-open"
                onClick={() => window.open(market.url, '_blank')}
              >
                Open
              </button>
              <button
                className="btn-add-basket"
                onClick={() => handleAddToBasket(market)}
              >
                Add to Basket
              </button>
            </div>
          </div>
        ))}
      </div>

      {basket.length > 0 && (
        <div className="basket-section">
          <div className="basket-header">
            <h3>Basket</h3>
            <button
              className="btn-open-next"
              onClick={handleOpenNextUnvisited}
              disabled={!basket.some(leg => !leg.visited)}
            >
              Open Next Unvisited
            </button>
          </div>
          <div className="basket-legs">
            {basket.map((leg) => (
              <div key={leg.id} className={`basket-leg ${leg.visited ? 'visited' : ''}`}>
                <div className="leg-content">
                  <div className="leg-title">{leg.title}</div>
                  {leg.category && <span className="leg-category">{leg.category}</span>}
                  <div className="leg-status">
                    {leg.visited ? '✓ Visited' : '○ Unvisited'}
                  </div>
                </div>
                <button
                  className="btn-remove-leg"
                  onClick={() => handleRemoveLeg(leg.id)}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
