import React, { useState, useEffect } from 'react';
import { getTrendingMarkets } from '../../utils/api';

// Types
interface TrendingMarket {
  market_id: string;
  question: string;
  market_slug?: string;
  tag_label?: string;
  last_price?: number;
  volume_24h?: number;
  open_interest?: number;
  trending_score?: number;
}

interface Category {
  id: string;
  label: string;
}

// Constants
const CATEGORIES: Category[] = [
  { id: 'all', label: 'All' },
  { id: 'politics', label: 'Politics' },
  { id: 'sports', label: 'Sports' },
  { id: 'crypto', label: 'Crypto' },
  { id: 'pop-culture', label: 'Pop Culture' },
  { id: 'business', label: 'Business' },
  { id: 'economy', label: 'Economy' },
  { id: 'science', label: 'Science' },
  { id: 'tech', label: 'Tech' },
];

// Icon Components
const TrendingUpIcon: React.FC = () => (
  <svg 
    width="14" 
    height="14" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="m22 7-8.5 8.5-5-5L2 17" />
    <path d="M16 7h6v6" />
  </svg>
);

const DollarIcon: React.FC = () => (
  <svg 
    width="14" 
    height="14" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <line x1="12" y1="2" x2="12" y2="22" />
    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
  </svg>
);

const ExternalLinkIcon: React.FC = () => (
  <svg 
    width="12" 
    height="12" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <polyline points="15 3 21 3 21 9" />
    <line x1="10" y1="14" x2="21" y2="3" />
  </svg>
);

// Utility Functions
const formatVolume = (volume?: number): string => {
  if (!volume) return '-';
  if (volume >= 1_000_000) return `$${(volume / 1_000_000).toFixed(1)}M`;
  if (volume >= 1_000) return `$${(volume / 1_000).toFixed(1)}K`;
  return `$${volume.toFixed(0)}`;
};

const calculatePrices = (lastPrice?: number): { yesPrice: number; noPrice: number } => {
  const yesPrice = lastPrice !== undefined ? Math.round(lastPrice * 100) : 50;
  const noPrice = 100 - yesPrice;
  return { yesPrice, noPrice };
};

// Main Component
export const TrendingTab: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [markets, setMarkets] = useState<TrendingMarket[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadMarkets = async (category: string): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Map frontend category IDs to backend category names
      const categoryMap: Record<string, string | undefined> = {
        'all': undefined,
        'politics': 'politics',
        'sports': 'sports',
        'crypto': 'crypto',
        'pop-culture': 'pop culture',
        'business': 'business',
        'economy': 'economy',
        'science': 'science',
        'tech': 'technology',
      };
      
      const backendCategory = categoryMap[category];
      console.log(`[TrendingTab] Loading markets for category: ${category} -> ${backendCategory || 'all'}`);
      
      const data = await getTrendingMarkets(backendCategory, 50); // Get more for better sorting
      const markets = data.markets || [];
      
      // Sort by trending_score (highest first) - backend should already do this, but ensure it
      const sortedMarkets = [...markets].sort((a, b) => {
        const scoreA = a.trending_score || a.open_interest || 0;
        const scoreB = b.trending_score || b.open_interest || 0;
        return scoreB - scoreA;
      });
      
      console.log(`[TrendingTab] Loaded ${sortedMarkets.length} markets, top score: ${sortedMarkets[0]?.trending_score || 'N/A'}`);
      setMarkets(sortedMarkets);
    } catch (e) {
      console.error('[TrendingTab] Error loading markets:', e);
      setError(e instanceof Error ? e.message : 'Failed to load trending markets');
      setMarkets([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadMarkets(selectedCategory);
  }, [selectedCategory]);

  const handleCategoryClick = (categoryId: string): void => {
    setSelectedCategory(categoryId);
  };

  const handleCategoryKeyDown = (e: React.KeyboardEvent, categoryId: string): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setSelectedCategory(categoryId);
    }
  };

  const handleRetryClick = (): void => {
    loadMarkets(selectedCategory);
  };

  const handleRetryKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      loadMarkets(selectedCategory);
    }
  };

  return (
    <div className="trending-tab">
      {/* Category Pills */}
      <div className="category-pills custom-scrollbar">
        {CATEGORIES.map((category) => (
          <button
            key={category.id}
            onClick={() => handleCategoryClick(category.id)}
            onKeyDown={(e) => handleCategoryKeyDown(e, category.id)}
            className={`category-pill ${selectedCategory === category.id ? 'active' : ''}`}
            aria-label={`Filter by ${category.label}`}
            aria-pressed={selectedCategory === category.id}
            tabIndex={0}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* Markets List */}
      <div className="markets-list custom-scrollbar">
        {/* Loading State */}
        {isLoading && (
          <>
            {[1, 2, 3].map((index) => (
              <div key={index} className="loading-skeleton" role="status" aria-label="Loading market">
                <div className="line" style={{ width: '75%' }} />
                <div className="line short" />
                <div className="line" style={{ width: '40%' }} />
              </div>
            ))}
          </>
        )}

        {/* Error State */}
        {!isLoading && error && (
          <div className="error-state" role="alert">
            <TrendingUpIcon />
            <p style={{ fontSize: '14px' }}>{error}</p>
            <button 
              className="btn-try-again"
              onClick={handleRetryClick}
              onKeyDown={handleRetryKeyDown}
              aria-label="Retry loading markets"
              tabIndex={0}
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && markets.length === 0 && (
          <div className="empty-state" role="status">
            <TrendingUpIcon />
            <p>No trending markets found</p>
          </div>
        )}

        {/* Markets */}
        {!isLoading && !error && markets.length > 0 && markets.map((market) => {
          const { yesPrice, noPrice } = calculatePrices(market.last_price);

          return (
            <div 
              key={market.market_id} 
              className="market-card"
              role="article"
              aria-label={`Market: ${market.question}`}
            >
              <p className="market-question">{market.question}</p>
              
              {(market.tag_label || market.canonical_category) && (
                <span className="market-category-tag" aria-label={`Category: ${market.tag_label || market.canonical_category}`}>
                  {market.tag_label || market.canonical_category}
                </span>
              )}
              
              <div className="market-yes-no" role="group" aria-label="Market prices">
                <div className="market-yes">
                  <div className="label">Yes</div>
                  <div className="val" aria-label={`Yes price: ${yesPrice} cents`}>{yesPrice}¢</div>
                </div>
                <div className="market-no">
                  <div className="label">No</div>
                  <div className="val" aria-label={`No price: ${noPrice} cents`}>{noPrice}¢</div>
                </div>
              </div>

              <div className="market-stats" role="group" aria-label="Market statistics">
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <DollarIcon />
                  <span aria-label={`Volume: ${formatVolume(market.volume_24h)}`}>
                    {formatVolume(market.volume_24h)}
                  </span>
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <TrendingUpIcon />
                  <span aria-label={`Open interest: ${formatVolume(market.open_interest)}`}>
                    {formatVolume(market.open_interest)}
                  </span>
                </span>
              </div>

              {market.market_slug && (
                <a
                  href={`https://polymarket.com/event/${market.market_slug}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-trade"
                  aria-label={`Trade ${market.question} on Polymarket`}
                  tabIndex={0}
                >
                  Trade <ExternalLinkIcon />
                </a>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
