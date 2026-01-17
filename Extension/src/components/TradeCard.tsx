import React from 'react';

interface TradeCardProps {
  title: string;
  url: string;
  side?: 'YES' | 'NO';
  amount?: number;
  topic?: string;
}

export const TradeCard: React.FC<TradeCardProps> = ({
  title,
  url,
  side,
  amount,
  topic,
}) => {
  return (
    <div className="trade-card">
      <div className="trade-card-header">
        <h3 className="trade-card-title">{title}</h3>
        {topic && <span className="trade-card-topic">{topic}</span>}
      </div>
      <div className="trade-card-url">{url}</div>
      <div className="trade-card-details">
        {side && (
          <div className="trade-card-side">
            <span className="label">Side:</span>
            <span className={`value side-${side.toLowerCase()}`}>{side}</span>
          </div>
        )}
        {amount !== undefined && (
          <div className="trade-card-amount">
            <span className="label">Amount:</span>
            <span className="value">${amount.toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  );
};
