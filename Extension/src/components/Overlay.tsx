import React, { useState, useEffect, useRef } from 'react';
import { TradeCard } from './TradeCard';
import { Tabs } from './Tabs';
import { BasketBuilder } from './BasketBuilder';
import type { RecommendationResponse, BasketLeg } from '../types';

interface OverlayProps {
  marketUrl: string;
  detectedSide?: 'YES' | 'NO';
  detectedAmount?: number;
  triggerType: 'hover' | 'ticket_open';
  onClose: () => void;
  onMinimize: () => void;
}

export const Overlay: React.FC<OverlayProps> = ({
  marketUrl,
  detectedSide,
  detectedAmount,
  triggerType,
  onClose,
  onMinimize,
}) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [basket, setBasket] = useState<BasketLeg[]>([]);
  const [activeTab, setActiveTab] = useState<'amplify' | 'hedge'>('amplify');
  const currentMarketUrl = useRef(marketUrl);
  const currentSide = useRef(detectedSide);
  const currentAmount = useRef(detectedAmount);
  
  // Initial load
  useEffect(() => {
    currentMarketUrl.current = marketUrl;
    currentSide.current = detectedSide;
    currentAmount.current = detectedAmount;
    loadRecommendations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Update if not pinned when props change
  useEffect(() => {
    if (!isPinned) {
      currentMarketUrl.current = marketUrl;
      currentSide.current = detectedSide;
      currentAmount.current = detectedAmount;
      loadRecommendations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [marketUrl, detectedSide, detectedAmount, isPinned]);
  
  async function loadRecommendations() {
    setLoading(true);
    try {
      const { getRecommendations } = await import('../utils/api');
      const { getLocalProfile } = await import('../utils/storage');
      
      const localProfile = await getLocalProfile();
      const response = await getRecommendations({
        primary: {
          url: currentMarketUrl.current,
          side: currentSide.current,
          amount: currentAmount.current,
          trigger_type: triggerType,
        },
        local_profile: localProfile,
      });
      
      setRecommendations(response);
      
      // Initialize basket with primary market if empty
      if (basket.length === 0) {
        setBasket([{
          id: response.primary_resolved.market_id,
          title: response.primary_resolved.title,
          url: currentMarketUrl.current,
          topic: response.primary_resolved.topics[0],
          visited: true,
        }]);
      } else {
        // Update primary market in basket
        setBasket(prevBasket => {
          const updated = [...prevBasket];
          if (updated.length > 0) {
            updated[0] = {
              id: response.primary_resolved.market_id,
              title: response.primary_resolved.title,
              url: currentMarketUrl.current,
              topic: response.primary_resolved.topics[0],
              visited: true,
            };
          }
          return updated;
        });
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  }
  
  function handlePinToggle() {
    setIsPinned(!isPinned);
  }
  
  function handleUnpinAndUpdate() {
    setIsPinned(false);
    if (onUpdatePrimary) {
      onUpdatePrimary(currentMarketUrl.current, currentSide.current, currentAmount.current);
    }
  }
  
  function handleMinimize() {
    setIsMinimized(true);
    onMinimize();
  }
  
  function handleAddLeg(market: { id: string; title: string; url: string; topic?: string }) {
    if (basket.some(leg => leg.id === market.id)) return;
    
    setBasket([...basket, {
      ...market,
      visited: false,
    }]);
  }
  
  function handleRemoveLeg(id: string) {
    setBasket(basket.filter(leg => leg.id !== id));
  }
  
  function handleOpenNextUnvisited() {
    const unvisited = basket.find(leg => !leg.visited);
    if (unvisited) {
      window.open(unvisited.url, '_blank');
      setBasket(basket.map(leg =>
        leg.id === unvisited.id ? { ...leg, visited: true } : leg
      ));
    }
  }
  
  if (isMinimized) {
    return (
      <div className="overlay-minimized">
        <button onClick={() => setIsMinimized(false)}>Restore</button>
      </div>
    );
  }
  
  return (
    <div className="overlay-container">
      <div className="overlay-header">
        <h2>Trade Assistant</h2>
        <div className="overlay-actions">
          <button
            onClick={handlePinToggle}
            className={`btn-pin ${isPinned ? 'pinned' : ''}`}
            title={isPinned ? 'Unpin to allow hover updates' : 'Pin current market'}
          >
            {isPinned ? '📌' : '📍'}
          </button>
          <button onClick={handleMinimize} className="btn-minimize">−</button>
          <button onClick={onClose} className="btn-close">×</button>
        </div>
      </div>
      
      <div className="overlay-content">
        {loading ? (
          <div className="skeleton-loading">
            <div className="skeleton-line"></div>
            <div className="skeleton-line"></div>
            <div className="skeleton-line"></div>
          </div>
        ) : recommendations ? (
          <>
            <TradeCard
              title={recommendations.primary_resolved.title}
              url={currentMarketUrl.current}
              side={currentSide.current}
              amount={currentAmount.current}
              topic={recommendations.primary_resolved.topics[0]}
            />
            
            <Tabs
              activeTab={activeTab}
              onTabChange={setActiveTab}
              amplify={recommendations.amplify}
              hedge={recommendations.hedge}
              onAddLeg={handleAddLeg}
            />
            
            <BasketBuilder
              legs={basket}
              onRemoveLeg={handleRemoveLeg}
              onOpenNextUnvisited={handleOpenNextUnvisited}
            />
          </>
        ) : (
          <div className="error-state">Failed to load recommendations</div>
        )}
      </div>
    </div>
  );
};
