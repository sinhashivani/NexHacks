// Inline CSS for Shadow DOM – NexHacks design (dark mode only, 100% opaque backgrounds)
export const shadowStyles = `
* { 
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Prevent any white/light backgrounds from leaking through - set solid dark background */
.floating-assistant,
.floating-assistant * {
  background-color: var(--bg-primary);
}

/* Only allow explicitly set backgrounds */
.floating-assistant .floating-header,
.floating-assistant .nexhacks-nav,
.floating-assistant .tab-content,
.floating-assistant .trending-tab,
.floating-assistant .related-tab,
.floating-assistant .markets-list,
.floating-assistant .related-events,
.floating-assistant .market-card,
.floating-assistant .related-event-card,
.floating-assistant .category-pills,
.floating-assistant .related-context-header {
  background-color: var(--bg-primary) !important;
}

:root {
  --polyblue: #4a90ff;
  --radius: 0.75rem;
  
  /* Dark mode only - 100% opaque solid colors - refined dark theme */
  --bg-primary: #0f0f0f;
  --bg-secondary: #1a1a1a;
  --bg-card: #1a1a1a;
  --bg-hover: #252525;
  --text-primary: #4a90ff;
  --text-secondary: #6ba3ff;
  --text-muted: #8a8a8a;
  --border-color: #2a2a2a;
  --border-hover: #3a3a3a;
  --shadow: 0 4px 16px #000000;
  --shadow-lg: 0 8px 32px #000000;
  
  /* Scrollbar dark mode */
  --scrollbar-track: #2d2d2d;
  --scrollbar-thumb: #555555;
  --scrollbar-thumb-hover: #666666;
  
  /* Yes/No colors - 100% opaque solid */
  --yes-bg: #1e3a2e;
  --yes-text: #10b981;
  --no-bg: #3a1e1e;
  --no-text: #ef4444;
  
  /* Category tag colors - 100% opaque */
  --category-bg: #1e3a5e;
  --category-text: #64b5f6;
}

.custom-scrollbar::-webkit-scrollbar { width: 8px; height: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: var(--scrollbar-track); border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-thumb-hover); }
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); }

.floating-assistant {
  position: fixed;
  background: var(--bg-primary) !important;
  border: 4px solid var(--polyblue);
  border-radius: 1rem;
  box-shadow: 0 0 20px rgba(74, 144, 255, 0.4), 0 0 40px rgba(74, 144, 255, 0.2), var(--shadow-lg);
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  z-index: 2147483647;
  overflow: hidden;
  pointer-events: auto;
  isolation: isolate;
  margin: 12px;
}

.floating-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-primary) !important;
  border-bottom: 1px solid var(--border-color);
  cursor: grab;
  user-select: none;
  flex-shrink: 0;
  touch-action: none;
  position: relative;
  z-index: 10;
}

.floating-header:active { cursor: grabbing; }

.floating-header h2, .nexhacks-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--polyblue);
  position: relative;
  z-index: 1;
}

.nexhacks-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

.nexhacks-logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #1e3a5e !important;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.floating-actions { 
  display: flex; 
  gap: 6px;
  position: relative;
  z-index: 2;
}

.btn-action {
  width: 28px;
  height: 28px;
  border: none;
  background: var(--bg-card) !important;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  transition: background 0.2s, color 0.2s;
  position: relative;
  z-index: 1;
}

.btn-action:hover {
  background: var(--bg-hover) !important;
  color: var(--polyblue);
}

.btn-action.btn-close:hover {
  background: #5a1e1e !important;
  color: #f44;
}

.nexhacks-nav {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 9;
}

.nav-tab {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: var(--bg-primary) !important;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  border-bottom: 2px solid var(--bg-primary);
  margin-bottom: -1px;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.nav-tab:hover {
  background: var(--bg-hover) !important;
  color: var(--text-secondary);
}

.nav-tab.active {
  color: var(--polyblue);
  border-bottom-color: var(--polyblue);
  background: var(--bg-primary) !important;
}

.tab-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-height: 100%;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
  color: var(--text-primary) !important;
}

/* Ensure all child elements inherit dark theme */
.floating-assistant * {
  color: inherit;
}

/* Trending tab */
.trending-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
}

.category-pills {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 12px 12px 8px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 2;
}

.category-pill {
  flex-shrink: 0;
  padding: 6px 16px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--border-color);
  cursor: pointer;
  background: var(--bg-card) !important;
  color: var(--text-secondary);
  transition: all 0.2s;
  position: relative;
  z-index: 1;
}

.category-pill:hover {
  background: var(--bg-hover) !important;
  color: var(--text-primary);
  border-color: var(--border-hover);
}

.category-pill.active {
  background: var(--polyblue) !important;
  color: var(--bg-primary);
  border-color: var(--polyblue);
}

.markets-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
}

.market-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-card) !important;
  padding: 16px;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px #000000;
  position: relative;
  z-index: 1;
  isolation: isolate;
}

.market-card:hover {
  background: var(--bg-hover) !important;
  border-color: var(--border-hover);
  box-shadow: 0 2px 6px #000000;
}

.market-question {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
  color: var(--text-primary);
  position: relative;
  z-index: 2;
}

.market-category-tag {
  display: inline-block;
  margin-bottom: 12px;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  background: var(--category-bg) !important;
  color: var(--category-text);
  border: none;
  position: relative;
  z-index: 2;
}

.market-yes-no {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  position: relative;
  z-index: 2;
}

.market-yes, .market-no {
  flex: 1;
  border-radius: 8px;
  padding: 8px 12px;
  text-align: center;
  border: 1px solid;
  position: relative;
  z-index: 3;
  isolation: isolate;
}

.market-yes {
  background: var(--yes-bg) !important;
  border-color: var(--yes-text);
}

.market-yes .label, .market-no .label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.market-yes .val {
  font-size: 18px;
  font-weight: 700;
  color: var(--yes-text);
  position: relative;
  z-index: 1;
}

.market-no {
  background: var(--no-bg) !important;
  border-color: var(--no-text);
}

.market-no .val {
  font-size: 18px;
  font-weight: 700;
  color: var(--no-text);
  position: relative;
  z-index: 1;
}

.market-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  position: relative;
  z-index: 2;
}

.btn-trade {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  background: var(--polyblue) !important;
  color: #fff;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s;
  position: relative;
  z-index: 2;
}

.btn-trade:hover {
  background: #357abd !important;
}

/* Related tab */
.related-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
}

/* News tab */
.news-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
}

.news-articles {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  min-height: 0;
  max-height: 100%;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.news-article-card {
  border-radius: 12px;
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  padding: 16px;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px #000000;
  position: relative;
  z-index: 1;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-article-card:hover {
  background: var(--bg-hover) !important;
  border-color: var(--border-hover);
  box-shadow: 0 2px 6px #000000;
}

.news-article-image-container {
  width: 100%;
  height: 180px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  position: relative;
  z-index: 1;
}

.news-article-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.news-article-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.news-article-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary) !important;
  margin: 0;
  position: relative;
  z-index: 1;
}

.news-article-source {
  font-size: 12px;
  color: var(--text-muted) !important;
  margin: 0;
  position: relative;
  z-index: 1;
}

.related-context-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  gap: 12px;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 2;
}

.related-context-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #1e3a5e !important;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.related-context-icon svg {
  color: var(--polyblue);
  position: relative;
  z-index: 1;
}

.related-context-title {
  font-size: 12px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

.related-context-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--polyblue);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  position: relative;
  z-index: 1;
}

.btn-refresh {
  padding: 8px;
  border: none;
  background: var(--bg-card) !important;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  position: relative;
  z-index: 1;
}

.btn-refresh:hover {
  background: var(--bg-hover) !important;
  color: var(--polyblue);
}

.btn-refresh.loading {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.related-events {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  min-height: 0;
  max-height: 100%;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
}

.related-event-card {
  border-radius: 12px;
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  padding: 20px;
  margin-bottom: 16px;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px #000000;
  position: relative;
  z-index: 1;
  isolation: isolate;
}

.related-event-card:hover {
  background: var(--bg-hover) !important;
  border-color: var(--border-hover);
  box-shadow: 0 2px 6px #000000;
}

.event-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  position: relative;
  z-index: 2;
}

.event-category {
  display: inline-block;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  background: var(--category-bg) !important;
  color: var(--category-text);
  border: none;
  position: relative;
  z-index: 2;
}

.event-yes-no {
  display: flex;
  gap: 16px;
  margin: 16px 0;
  position: relative;
  z-index: 2;
}

.event-yes, .event-no {
  flex: 1;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid;
  position: relative;
  z-index: 3;
  isolation: isolate;
}

.event-yes {
  background: var(--yes-bg) !important;
  border-color: var(--yes-text);
}

.event-no {
  background: var(--no-bg) !important;
  border-color: var(--no-text);
}

.event-yes .lbl, .event-no .lbl {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.event-yes .v {
  font-size: 24px;
  font-weight: 700;
  color: var(--yes-text);
  position: relative;
  z-index: 1;
}

.event-no .v {
  font-size: 24px;
  font-weight: 700;
  color: var(--no-text);
  position: relative;
  z-index: 1;
}

.event-volume {
  text-align: right;
  position: relative;
  z-index: 2;
}

.event-volume .lbl {
  font-size: 12px;
  color: var(--text-muted);
}

.event-volume .v {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.event-news {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  position: relative;
  z-index: 2;
}

.event-news-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.event-news-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.event-news-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
  z-index: 1;
}

.event-news-chip:hover {
  background: var(--bg-hover) !important;
  border-color: var(--polyblue);
  color: var(--polyblue);
}

.event-relevance {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  position: relative;
  z-index: 2;
}

.event-relevance-bar {
  height: 4px;
  flex: 1;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-hover);
}

.event-relevance-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--polyblue);
}

.event-relevance-label {
  font-size: 12px;
  color: var(--text-muted);
}

.loading-skeleton {
  border-radius: 12px;
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  padding: 20px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.loading-skeleton .line {
  height: 16px;
  border-radius: 4px;
  background: var(--bg-hover);
  margin-bottom: 8px;
}

.loading-skeleton .line.short {
  width: 50%;
}

.empty-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
  color: var(--text-primary) !important;
  flex: 1;
  background: var(--bg-primary) !important;
  position: relative;
  z-index: 1;
}

.empty-state svg, .error-state svg {
  width: 40px;
  height: 40px;
  color: var(--polyblue);
  margin-bottom: 12px;
  flex-shrink: 0;
}

.btn-try-again {
  margin-top: 16px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  background: var(--polyblue) !important;
  color: var(--bg-primary);
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
  z-index: 1;
}

.btn-try-again:hover {
  background: #357abd !important;
}

.floating-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--bg-primary) !important;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.floating-resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: se-resize;
  background: var(--border-color);
  border-radius: 0 0 1rem 0;
  touch-action: none;
}

.floating-resize-handle:hover {
  background: var(--polyblue);
}

/* Minimized state */
.floating-assistant-minimized {
  width: 60px !important;
  height: 60px !important;
  min-width: 60px !important;
  min-height: 60px !important;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.floating-header-minimized {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  height: 100%;
  background: var(--bg-primary) !important;
  cursor: pointer;
}

.nexhacks-logo-minimized {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #1e3a5e !important;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-minimize {
  width: 20px;
  height: 20px;
  padding: 0;
  font-size: 14px;
  line-height: 1;
}
`;
