import React, { useState, useEffect } from 'react';
import { getMarketHistory, addToHistory } from '../utils/storage';
import { savePinnedOrder } from '../utils/storage';
import type { MarketHistoryItem, PinnedOrder } from '../types';
import './History.css';

export const History: React.FC = () => {
  const [history, setHistory] = useState<MarketHistoryItem[]>([]);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadHistory();
    
    // Track current page view
    const currentMarket = {
      title: document.querySelector('h1')?.textContent?.trim() || 'Market',
      url: window.location.href,
      timestamp: Date.now(),
    };
    
    addToHistory(currentMarket);
    loadHistory();
  }, []);

  async function loadHistory() {
    const saved = await getMarketHistory();
    setHistory(saved);
  }

  async function handlePinFromHistory(item: MarketHistoryItem) {
    const newOrder: PinnedOrder = {
      id: `pin-${Date.now()}`,
      title: item.title,
      url: item.url,
      timestamp: Date.now(),
      notes: '',
    };
    
    await savePinnedOrder(newOrder);
    // Reload pinned orders in parent (would need callback, but for now just save)
  }

  if (history.length === 0) {
    return null;
  }

  const displayHistory = expanded ? history : history.slice(0, 5);

  return (
    <div className="history-section">
      <div className="history-header">
        <h3>Recent History</h3>
        {history.length > 5 && (
          <button
            className="btn-expand"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Show Less' : `Show All (${history.length})`}
          </button>
        )}
      </div>

      <div className="history-list">
        {displayHistory.map((item, index) => (
          <div key={`${item.url}-${item.timestamp}`} className="history-item">
            <div className="history-item-title">{item.title}</div>
            <div className="history-item-url">{item.url}</div>
            <div className="history-item-actions">
              <button
                className="btn-open-history"
                onClick={() => window.open(item.url, '_blank')}
              >
                Open
              </button>
              <button
                className="btn-pin-history"
                onClick={() => handlePinFromHistory(item)}
              >
                Pin
              </button>
            </div>
            <div className="history-item-timestamp">
              {new Date(item.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
