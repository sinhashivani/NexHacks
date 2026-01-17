import React from 'react';
import type { BasketLeg } from '../types';

interface BasketBuilderProps {
  legs: BasketLeg[];
  onRemoveLeg: (id: string) => void;
  onOpenNextUnvisited: () => void;
}

export const BasketBuilder: React.FC<BasketBuilderProps> = ({
  legs,
  onRemoveLeg,
  onOpenNextUnvisited,
}) => {
  const hasUnvisited = legs.some(leg => !leg.visited);
  
  return (
    <div className="basket-builder">
      <div className="basket-header">
        <h3>Basket Builder</h3>
        {hasUnvisited && (
          <button className="btn-open-next" onClick={onOpenNextUnvisited}>
            Open Next Unvisited
          </button>
        )}
      </div>
      
      <div className="basket-legs">
        {legs.map((leg) => (
          <div key={leg.id} className={`basket-leg ${leg.visited ? 'visited' : ''}`}>
            <div className="leg-content">
              <div className="leg-title">{leg.title}</div>
              {leg.topic && <span className="leg-topic">{leg.topic}</span>}
              <div className="leg-status">
                {leg.visited ? (
                  <span className="status-visited">✓ Visited</span>
                ) : (
                  <span className="status-unvisited">○ Unvisited</span>
                )}
              </div>
            </div>
            {legs.length > 1 && (
              <button
                className="btn-remove-leg"
                onClick={() => onRemoveLeg(leg.id)}
                title="Remove leg"
              >
                ×
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
