import React from 'react';
import { MarketList } from './MarketList';
import type { MarketRecommendation } from '../types';

interface TabsProps {
  activeTab: 'amplify' | 'hedge';
  onTabChange: (tab: 'amplify' | 'hedge') => void;
  amplify: MarketRecommendation[];
  hedge: MarketRecommendation[];
  onAddLeg: (market: { id: string; title: string; url: string; topic?: string }) => void;
}

export const Tabs: React.FC<TabsProps> = ({
  activeTab,
  onTabChange,
  amplify,
  hedge,
  onAddLeg,
}) => {
  return (
    <div className="tabs-container">
      <div className="tabs-header">
        <button
          className={`tab-button ${activeTab === 'amplify' ? 'active' : ''}`}
          onClick={() => onTabChange('amplify')}
        >
          Amplify
        </button>
        <button
          className={`tab-button ${activeTab === 'hedge' ? 'active' : ''}`}
          onClick={() => onTabChange('hedge')}
        >
          Hedge
        </button>
      </div>
      
      <div className="tabs-content">
        {activeTab === 'amplify' ? (
          <MarketList markets={amplify} onAddLeg={onAddLeg} />
        ) : (
          <MarketList markets={hedge} onAddLeg={onAddLeg} />
        )}
      </div>
    </div>
  );
};
