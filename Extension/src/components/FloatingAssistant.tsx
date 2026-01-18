import React, { useEffect, useRef, useState } from 'react';
import type { CurrentMarket, OverlayState } from '../types';
import { TrendingTab } from './tabs/TrendingTab';
import { RelatedTab } from './tabs/RelatedTab';
import { NewsTab } from './tabs/NewsTab';
import './FloatingAssistant.css';

// Types
type TabId = 'trending' | 'related' | 'news';

interface FloatingAssistantProps {
  currentMarket: CurrentMarket;
  state: OverlayState;
  onStateChange: (state: Partial<OverlayState>) => void;
}

interface DragState {
  clientX: number;
  clientY: number;
}

interface ResizeState {
  x: number;
  y: number;
  width: number;
  height: number;
  clientX: number;
  clientY: number;
}

// Icon Components
const NexHacksLogo: React.FC = () => (
  <svg 
    viewBox="0 0 24 24" 
    fill="none" 
    width="20" 
    height="20" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M12 2L2 7l10 5 10-5-10-5z" />
    <path d="M2 17l10 5 10-5" opacity="0.6" />
    <path d="M2 12l10 5 10-5" opacity="0.8" />
  </svg>
);

const TrendingNavIcon: React.FC = () => (
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
    <path d="m22 7-8.5 8.5-5-5L2 17" />
    <path d="M16 7h6v6" />
  </svg>
);

const RelatedNavIcon: React.FC = () => (
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
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </svg>
);

const NewsNavIcon: React.FC = () => (
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
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" />
    <path d="M18 14h-8" />
    <path d="M15 18h-5" />
    <path d="M10 6h8v4h-8V6Z" />
  </svg>
);

// Main Component
export const FloatingAssistant: React.FC<FloatingAssistantProps> = ({
  currentMarket,
  state,
  onStateChange,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>('trending');
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isResizing, setIsResizing] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<DragState>({ clientX: 0, clientY: 0 });
  const [resizeStart, setResizeStart] = useState<ResizeState>({ 
    x: 0, 
    y: 0, 
    width: 0, 
    height: 0, 
    clientX: 0, 
    clientY: 0 
  });

  const assistantRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  // Auto-detect market pages and switch to Related tab
  useEffect(() => {
    const isMarketPage = window.location.href.includes('/event/') || 
                         window.location.href.includes('/market/') ||
                         currentMarket.title !== 'Market';
    
    if (isMarketPage && currentMarket.title && currentMarket.title !== 'Market') {
      console.log('[FloatingAssistant] Detected market page:', currentMarket.title);
      setActiveTab('related');
    }
  }, [currentMarket.title, currentMarket.url]);

  // Early return helper
  const isFloatingMode = (): boolean => state.layoutMode === 'floating';

  // Event Handlers - Drag
  const handleHeaderPointerDown = (e: React.PointerEvent): void => {
    if ((e.target as HTMLElement).closest('.floating-actions')) return;
    if (!isFloatingMode()) return;
    
    setIsDragging(true);
    setDragStart({ clientX: e.clientX, clientY: e.clientY });
    if (headerRef.current) {
      headerRef.current.setPointerCapture(e.pointerId);
    }
  };

  useEffect(() => {
    if (!isDragging || !isFloatingMode()) return;

    const handlePointerMove = (e: PointerEvent): void => {
      const deltaX = e.clientX - dragStart.clientX;
      const deltaY = e.clientY - dragStart.clientY;
      const newX = Math.max(0, Math.min(state.x + deltaX, window.innerWidth - state.width));
      const newY = Math.max(0, Math.min(state.y + deltaY, window.innerHeight - state.height));
      
      onStateChange({ x: newX, y: newY });
      setDragStart({ clientX: e.clientX, clientY: e.clientY });
    };

    const handlePointerUp = (e: PointerEvent): void => {
      setIsDragging(false);
      try {
        if (headerRef.current) {
          headerRef.current.releasePointerCapture(e.pointerId);
        }
      } catch (_) {
        // Ignore errors from releasePointerCapture
      }
    };

    document.addEventListener('pointermove', handlePointerMove, { passive: true });
    document.addEventListener('pointerup', handlePointerUp, { passive: true });

    return () => {
      document.removeEventListener('pointermove', handlePointerMove);
      document.removeEventListener('pointerup', handlePointerUp);
    };
  }, [isDragging, dragStart, state, onStateChange]);

  // Event Handlers - Resize
  const handleResizePointerDown = (e: React.PointerEvent): void => {
    if (!isFloatingMode()) return;
    
    e.preventDefault();
    setIsResizing(true);
    setResizeStart({ 
      x: state.x, 
      y: state.y, 
      width: state.width, 
      height: state.height, 
      clientX: e.clientX, 
      clientY: e.clientY 
    });
    
    if (assistantRef.current) {
      assistantRef.current.setPointerCapture(e.pointerId);
    }
  };

  useEffect(() => {
    if (!isResizing || !isFloatingMode()) return;

    const handlePointerMove = (e: PointerEvent): void => {
      const newWidth = Math.max(280, Math.min(560, resizeStart.width - (e.clientX - resizeStart.clientX)));
      const newHeight = Math.max(200, resizeStart.height + (e.clientY - resizeStart.clientY));
      onStateChange({ width: newWidth, height: newHeight });
    };

    const handlePointerUp = (e: PointerEvent): void => {
      setIsResizing(false);
      try {
        if (assistantRef.current) {
          assistantRef.current.releasePointerCapture(e.pointerId);
        }
      } catch (_) {
        // Ignore errors from releasePointerCapture
      }
    };

    document.addEventListener('pointermove', handlePointerMove, { passive: true });
    document.addEventListener('pointerup', handlePointerUp, { passive: true });

    return () => {
      document.removeEventListener('pointermove', handlePointerMove);
      document.removeEventListener('pointerup', handlePointerUp);
    };
  }, [isResizing, resizeStart, state, onStateChange]);

  // Event Handlers - UI Actions
  const handleCloseClick = (): void => {
    onStateChange({ open: false });
  };

  const handleCloseKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onStateChange({ open: false });
    }
  };

  const handleTabClick = (tabId: TabId): void => {
    setActiveTab(tabId);
  };

  const handleTabKeyDown = (e: React.KeyboardEvent, tabId: TabId): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setActiveTab(tabId);
    }
  };


  // Computed Values
  const showResizeHandle = isFloatingMode() && !state.minimized;
  const headerCursor = isFloatingMode() ? (isDragging ? 'grabbing' : 'grab') : 'default';
  const assistantCursor = isDragging ? 'grabbing' : isResizing ? 'se-resize' : 'auto';

  // Main Panel
  return (
    <div
      ref={assistantRef}
      className="floating-assistant"
      style={{
        width: `${state.width}px`,
        height: state.layoutMode === 'docked' ? 'auto' : `${state.height}px`,
        cursor: assistantCursor,
        userSelect: isDragging ? 'none' : 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}
      role="dialog"
      aria-label="NexHacks Polymarket Assistant"
    >
      {/* Header */}
      <div
        ref={headerRef}
        className="floating-header"
        onPointerDown={handleHeaderPointerDown}
        style={{ cursor: headerCursor }}
        role="banner"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="nexhacks-logo" aria-label="NexHacks logo">
            <NexHacksLogo />
          </div>
          <div>
            <h2 className="nexhacks-title">NexHacks</h2>
            <p className="nexhacks-subtitle">Polymarket Companion</p>
          </div>
        </div>
        <div className="floating-actions">
            <button
              className="btn-action btn-close"
              onClick={handleCloseClick}
              onKeyDown={handleCloseKeyDown}
              aria-label="Close assistant"
              title="Close"
              tabIndex={0}
            >
              ✕
            </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="nexhacks-nav" role="tablist" aria-label="Market tabs">
        <button
          className={`nav-tab ${activeTab === 'trending' ? 'active' : ''}`}
          onClick={() => handleTabClick('trending')}
          onKeyDown={(e) => handleTabKeyDown(e, 'trending')}
          role="tab"
          aria-selected={activeTab === 'trending'}
          aria-controls="trending-panel"
          aria-label="Trending markets"
          tabIndex={0}
        >
          <TrendingNavIcon /> Trending
        </button>
        <button
          className={`nav-tab ${activeTab === 'related' ? 'active' : ''}`}
          onClick={() => handleTabClick('related')}
          onKeyDown={(e) => handleTabKeyDown(e, 'related')}
          role="tab"
          aria-selected={activeTab === 'related'}
          aria-controls="related-panel"
          aria-label="Related markets"
          tabIndex={0}
        >
          <RelatedNavIcon /> Related
        </button>
        <button
          className={`nav-tab ${activeTab === 'news' ? 'active' : ''}`}
          onClick={() => handleTabClick('news')}
          onKeyDown={(e) => handleTabKeyDown(e, 'news')}
          role="tab"
          aria-selected={activeTab === 'news'}
          aria-controls="news-panel"
          aria-label="News articles"
          tabIndex={0}
        >
          <NewsNavIcon /> News
        </button>
      </nav>

      {/* Tab Content */}
      <main className="tab-content" role="tabpanel" id={`${activeTab}-panel`}>
        {activeTab === 'trending' && <TrendingTab />}
        {activeTab === 'related' && <RelatedTab />}
        {activeTab === 'news' && <NewsTab />}
      </main>

      {/* Resize Handle */}
      {showResizeHandle && (
        <div
          className="floating-resize-handle"
          onPointerDown={handleResizePointerDown}
          style={{ cursor: 'se-resize' }}
          role="separator"
          aria-label="Resize assistant"
          aria-valuemin={200}
          aria-valuemax={800}
          aria-valuenow={state.height}
          tabIndex={0}
        />
      )}
    </div>
  );
};
