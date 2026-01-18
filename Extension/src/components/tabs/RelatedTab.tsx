import React, { useState, useEffect } from 'react';
import { getSimilarMarkets, getRelatedMarkets, getNews, type NewsArticle } from '../../utils/api';
import { scrapeCurrentMarket } from '../../utils/marketScraper';

// Types
interface RelatedMarket {
  market_id: string;
  question: string;
  market_slug?: string;
  tag_label?: string;
  last_price?: number;
  cosine_similarity?: number;
  relationship_type?: string;
  relationship_strength?: number;
  description?: string;
}

interface CurrentMarketInfo {
  title: string;
  url: string;
}

// Icon Components
const GlobeIcon: React.FC = () => (
  <svg 
    width="16" 
    height="16" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <circle cx="12" cy="12" r="10" />
    <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
    <path d="M2 12h20" />
  </svg>
);

const RefreshIcon: React.FC = () => (
  <svg 
    width="16" 
    height="16" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
    <path d="M3 3v5h5" />
  </svg>
);

const TrendingUpIcon: React.FC = () => (
  <svg 
    width="40" 
    height="40" 
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
const calculatePrices = (lastPrice?: number): { yesPrice: number; noPrice: number } => {
  const yesPrice = lastPrice !== undefined ? Math.round(lastPrice * 100) : 50;
  const noPrice = 100 - yesPrice;
  return { yesPrice, noPrice };
};

const formatRelevance = (market: RelatedMarket): number => {
  if (market.cosine_similarity !== undefined) return market.cosine_similarity;
  if (market.relationship_strength !== undefined) return market.relationship_strength;
  return 0.5;
};

// Main Component
export const RelatedTab: React.FC = () => {
  const [currentMarket, setCurrentMarket] = useState<CurrentMarketInfo | null>(null);
  const [markets, setMarkets] = useState<RelatedMarket[]>([]);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadRelatedMarkets = async (): Promise<void> => {
    console.log('[RelatedTab] ========================================');
    console.log('[RelatedTab] LOADING RELATED MARKETS');
    console.log('[RelatedTab] ========================================');
    
    setIsLoading(true);
    setError(null);

    try {
      // Get current market from page
      const market = scrapeCurrentMarket();
      console.log('[RelatedTab] Scraped market from page:', market.title);
      console.log('[RelatedTab] Market URL:', market.url);
      
      setCurrentMarket({ title: market.title, url: market.url });

      if (!market.title || market.title === 'Market') {
        console.warn('[RelatedTab] No valid market detected');
        setError('No market detected on this page');
        setMarkets([]);
        return;
      }
      
      console.log('[RelatedTab] Starting data fetch with cosine similarity...');

      // Try similar markets FIRST (uses fuzzy text matching)
      try {
        const similarData = await getSimilarMarkets(market.title);
        if (similarData?.similar_markets && similarData.similar_markets.length > 0) {
          console.log('[RelatedTab] Found similar markets:', similarData.similar_markets.length);
          setMarkets(similarData.similar_markets);
          
          // Fetch news in parallel
          try {
            const newsData = await getNews(market.title);
            if (newsData?.articles) {
              console.log('[RelatedTab] Loaded news articles:', newsData.articles.length);
              setNewsArticles(newsData.articles);
            }
          } catch (e) {
            console.log('[RelatedTab] News not available:', e);
          }
          return;
        }
      } catch (e) {
        console.log('[RelatedTab] Similar markets not available, trying related markets');
      }

      // Fallback to related markets (exact event_title match)
      try {
        const relatedData = await getRelatedMarkets(undefined, market.title, 10);
        if (relatedData?.markets && relatedData.markets.length > 0) {
          setMarkets(relatedData.markets);
        } else {
          setMarkets([]);
          setError('No related markets found');
        }
      } catch (e) {
        console.error('[RelatedTab] Error fetching related markets:', e);
        setError('No related markets found');
        setMarkets([]);
      }

    } catch (e) {
      console.error('[RelatedTab] Error:', e);
      setError(e instanceof Error ? e.message : 'Failed to fetch related markets');
      setMarkets([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRelatedMarkets();
  }, []);

  const handleRefreshClick = (): void => {
    loadRelatedMarkets();
  };

  const handleRefreshKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      loadRelatedMarkets();
    }
  };

  const handleRetryClick = (): void => {
    loadRelatedMarkets();
  };

  const handleRetryKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      loadRelatedMarkets();
    }
  };

  return (
    <div className="related-tab">
      {/* Context Header */}
      <div className="related-context-header">
        <div className="related-context-icon" aria-hidden="true">
          <GlobeIcon />
        </div>
        <div style={{ minWidth: 0, flex: 1 }}>
          <p className="related-context-title">Detected from page</p>
          <p className="related-context-name" aria-label={`Current market: ${currentMarket?.title ?? 'Scanning...'}`}>
            {currentMarket?.title ?? 'Scanning...'}
          </p>
        </div>
        <button 
          className={`btn-refresh ${isLoading ? 'loading' : ''}`}
          onClick={handleRefreshClick}
          onKeyDown={handleRefreshKeyDown}
          disabled={isLoading}
          aria-label="Refresh related markets"
          aria-busy={isLoading}
          tabIndex={0}
        >
          <RefreshIcon />
        </button>
      </div>

      {/* Markets List */}
      <div className="related-events custom-scrollbar">
        {/* Loading State */}
        {isLoading && (
          <>
            {[1, 2, 3].map((index) => (
              <div key={index} className="loading-skeleton" role="status" aria-label="Loading related market">
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
              aria-label="Retry loading related markets"
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
            <p>No related markets found</p>
          </div>
        )}

        {/* News Articles Section */}
        {!isLoading && newsArticles.length > 0 && (
          <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-primary)' }}>
              📰 Related News
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {newsArticles.map((article, index) => (
                <div 
                  key={index}
                  style={{
                    display: 'flex',
                    gap: '12px',
                    padding: '12px',
                    background: 'var(--bg-card)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)',
                  }}
                >
                  {article.image && (
                    <img 
                      src={article.image} 
                      alt="" 
                      style={{
                        width: '80px',
                        height: '60px',
                        objectFit: 'cover',
                        borderRadius: '6px',
                        flexShrink: 0,
                      }}
                    />
                  )}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ 
                      fontSize: '13px', 
                      fontWeight: '500', 
                      lineHeight: '1.4',
                      marginBottom: '4px',
                      color: 'var(--text-primary)',
                    }}>
                      {article.title}
                    </p>
                    <p style={{ 
                      fontSize: '11px', 
                      color: 'var(--text-muted)',
                    }}>
                      {article.name}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Related Markets */}
        {!isLoading && !error && markets.length > 0 && markets.map((market) => {
          const { yesPrice, noPrice } = calculatePrices(market.last_price);
          const relevance = formatRelevance(market);

          return (
            <div 
              key={market.market_id} 
              className="related-event-card"
              role="article"
              aria-label={`Related market: ${market.question}`}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                <h3 className="event-title">{market.question}</h3>
                {market.tag_label && (
                  <span className="event-category" aria-label={`Category: ${market.tag_label}`}>
                    {market.tag_label}
                  </span>
                )}
                {market.relationship_type && (
                  <span className="event-category" aria-label={`Relationship: ${market.relationship_type}`}>
                    {market.relationship_type}
                  </span>
                )}
              </div>

              <div className="event-yes-no" role="group" aria-label="Market prices">
                <div className="event-yes">
                  <span className="lbl">Yes</span>
                  <span className="v" aria-label={`Yes price: ${yesPrice} cents`}>{yesPrice}¢</span>
                </div>
                <div className="event-no">
                  <span className="lbl">No</span>
                  <span className="v" aria-label={`No price: ${noPrice} cents`}>{noPrice}¢</span>
                </div>
              </div>

              {market.description && (
                <div className="event-news">
                  <p className="event-news-label">Description</p>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {market.description}
                  </p>
                </div>
              )}

              <div className="event-relevance" role="group" aria-label={`Match strength: ${Math.round(relevance * 100)} percent`}>
                <div className="event-relevance-bar" aria-hidden="true">
                  <div className="event-relevance-fill" style={{ width: `${relevance * 100}%` }} />
                </div>
                <span className="event-relevance-label">
                  {Math.round(relevance * 100)}% match
                </span>
              </div>

              {market.market_slug && (
                <a
                  href={`https://polymarket.com/event/${market.market_slug}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-trade"
                  style={{ marginTop: '12px' }}
                  aria-label={`View ${market.question} on Polymarket`}
                  tabIndex={0}
                >
                  View Market <ExternalLinkIcon />
                </a>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
