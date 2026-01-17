import React, { useState, useEffect, useRef } from 'react';
import { TradeCard } from './TradeCard';
import { Recommendations } from './Recommendations';
import { PinnedOrders } from './PinnedOrders';
import { History } from './History';
import type { CurrentMarket, OverlayState } from '../types';
import './Panel.css';

interface PanelProps {
  currentMarket: CurrentMarket;
  onStateChange: (state: OverlayState) => void;
  initialState: OverlayState;
}

export const Panel: React.FC<PanelProps> = ({
  currentMarket,
  onStateChange,
  initialState,
}) => {
  const [isMinimized, setIsMinimized] = useState(initialState.minimized);
  const [isResizing, setIsResizing] = useState(false);
  const [width, setWidth] = useState(initialState.width);
  const panelRef = useRef<HTMLDivElement>(null);
  const resizeStartX = useRef<number>(0);
  const resizeStartWidth = useRef<number>(0);

  useEffect(() => {
    setWidth(initialState.width);
    setIsMinimized(initialState.minimized);
  }, [initialState]);

  useEffect(() => {
    // Update page margin when panel state changes
    updatePageMargin();
  }, [width, isMinimized]);

  function updatePageMargin() {
    const margin = isMinimized ? 60 : width;
    document.body.style.marginRight = `${margin}px`;
  }

  function handleResizeStart(e: React.MouseEvent) {
    e.preventDefault();
    setIsResizing(true);
    resizeStartX.current = e.clientX;
    resizeStartWidth.current = width;
    
    document.addEventListener('mousemove', handleResizeMove);
    document.addEventListener('mouseup', handleResizeEnd);
  }

  function handleResizeMove(e: MouseEvent) {
    if (!isResizing) return;
    
    const diff = resizeStartX.current - e.clientX; // Inverted because we're resizing from right
    const newWidth = Math.max(280, Math.min(560, resizeStartWidth.current + diff));
    setWidth(newWidth);
  }

  function handleResizeEnd() {
    setIsResizing(false);
    document.removeEventListener('mousemove', handleResizeMove);
    document.removeEventListener('mouseup', handleResizeEnd);
    
    // Save state
    onStateChange({
      open: true,
      minimized: isMinimized,
      width,
    });
  }

  function handleMinimize() {
    const newMinimized = !isMinimized;
    setIsMinimized(newMinimized);
    // Minimize sets minimized=true, open stays true
    onStateChange({
      open: true,
      minimized: newMinimized,
      width,
    });
  }

  function handleClose() {
    document.body.style.marginRight = '0';
    // Close sets open=false, minimized=false
    onStateChange({
      open: false,
      minimized: false,
      width,
    });
  }

  if (isMinimized) {
    return (
      <div className="panel-minimized" style={{ width: '60px' }}>
        <div className="panel-header-minimized">
          <button onClick={handleMinimize} className="btn-restore" title="Restore">→</button>
          <button onClick={handleClose} className="btn-close">×</button>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={panelRef}
      className="panel-container"
      style={{ width: `${width}px` }}
    >
      <div
        className="panel-resize-handle"
        onMouseDown={handleResizeStart}
      />
      
      <div className="panel-content">
        <div className="panel-header">
          <h2>Trade Assistant</h2>
          <div className="panel-actions">
            <button onClick={handleMinimize} className="btn-minimize">−</button>
            <button onClick={handleClose} className="btn-close">×</button>
          </div>
        </div>
        
        <div className="panel-body">
          <TradeCard
            title={currentMarket.title}
            url={currentMarket.url}
            side={currentMarket.side}
            amount={currentMarket.amount}
          />
          
          <Recommendations currentUrl={currentMarket.url} />
          
          <PinnedOrders />
          
          <History />
        </div>
      </div>
    </div>
  );
};
