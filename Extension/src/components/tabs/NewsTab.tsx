import React, { useState, useEffect } from 'react';
import { getNews, type NewsArticle } from '../../utils/api';
import { scrapeCurrentMarket } from '../../utils/marketScraper';

// Types
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

const NewsIcon: React.FC = () => (
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
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" />
    <path d="M18 14h-8" />
    <path d="M15 18h-5" />
    <path d="M10 6h8v4h-8V6Z" />
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

// Main Component
export const NewsTab: React.FC = () => {
  const [currentMarket, setCurrentMarket] = useState<CurrentMarketInfo | null>(null);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadNews = async (): Promise<void> => {
    console.log('[NewsTab] ========================================');
    console.log('[NewsTab] LOADING NEWS ARTICLES');
    console.log('[NewsTab] ========================================');
    
    setIsLoading(true);
    setError(null);

    try {
      // Get current market from page
      const market = scrapeCurrentMarket();
      console.log('[NewsTab] Scraped market from page:', market.title);
      console.log('[NewsTab] Market URL:', market.url);
      
      setCurrentMarket({ title: market.title, url: market.url });

      if (!market.title || market.title === 'Market') {
        console.warn('[NewsTab] No valid market detected');
        setError('No market detected on this page. Please navigate to a market page.');
        setArticles([]);
        return;
      }
      
      console.log('[NewsTab] Fetching news for:', market.title);

      // Fetch news articles
      const newsData = await getNews(market.title);
      if (newsData?.articles && newsData.articles.length > 0) {
        console.log('[NewsTab] Loaded news articles:', newsData.articles.length);
        setArticles(newsData.articles);
      } else {
        console.log('[NewsTab] No news articles found');
        setArticles([]);
        setError('No news articles found for this market');
      }

    } catch (e) {
      console.error('[NewsTab] Error:', e);
      setError(e instanceof Error ? e.message : 'Failed to fetch news articles');
      setArticles([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNews();
  }, []);

  const handleRefreshClick = (): void => {
    loadNews();
  };

  const handleRefreshKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      loadNews();
    }
  };

  const handleRetryClick = (): void => {
    loadNews();
  };

  const handleRetryKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      loadNews();
    }
  };

  return (
    <div className="news-tab">
      {/* Context Header */}
      <div className="related-context-header">
        <div className="related-context-icon" aria-hidden="true">
          <GlobeIcon />
        </div>
        <div style={{ minWidth: 0, flex: 1 }}>
          <p className="related-context-title">News for</p>
          <p className="related-context-name" aria-label={`Current market: ${currentMarket?.title ?? 'Scanning...'}`}>
            {currentMarket?.title ?? 'Scanning...'}
          </p>
        </div>
        <button 
          className={`btn-refresh ${isLoading ? 'loading' : ''}`}
          onClick={handleRefreshClick}
          onKeyDown={handleRefreshKeyDown}
          disabled={isLoading}
          aria-label="Refresh news articles"
          aria-busy={isLoading}
          tabIndex={0}
        >
          <RefreshIcon />
        </button>
      </div>

      {/* News Articles List */}
      <div className="news-articles custom-scrollbar">
        {/* Loading State */}
        {isLoading && (
          <>
            {[1, 2, 3].map((index) => (
              <div key={index} className="loading-skeleton" role="status" aria-label="Loading news article">
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
            <NewsIcon />
            <p style={{ fontSize: '14px' }}>{error}</p>
            <button 
              className="btn-try-again"
              onClick={handleRetryClick}
              onKeyDown={handleRetryKeyDown}
              aria-label="Retry loading news"
              tabIndex={0}
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && articles.length === 0 && (
          <div className="empty-state" role="status">
            <NewsIcon />
            <p>No news articles found</p>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
              Try refreshing or check back later
            </p>
          </div>
        )}

        {/* News Articles */}
        {!isLoading && !error && articles.length > 0 && articles.map((article, index) => (
          <div 
            key={index}
            className="news-article-card"
            role="article"
            aria-label={`News article: ${article.title}`}
          >
            {article.image && (
              <div className="news-article-image-container">
                <img 
                  src={article.image} 
                  alt="" 
                  className="news-article-image"
                  onError={(e) => {
                    // Hide image on error
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
            )}
            
            <div className="news-article-content">
              <h3 className="news-article-title">{article.title}</h3>
              
              {article.name && (
                <p className="news-article-source" aria-label={`Source: ${article.name}`}>
                  {article.name}
                </p>
              )}
              
              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-trade"
                  style={{ marginTop: '12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                  aria-label={`Read article: ${article.title}`}
                  tabIndex={0}
                >
                  Read Article <ExternalLinkIcon />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
