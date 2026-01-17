// Inline CSS for Shadow DOM - Floating overlay styles
export const shadowStyles = `
* {
  box-sizing: border-box;
}

/* Floating Assistant Styles */
.floating-assistant {
  position: fixed;
  background: white;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  z-index: 2147483647;
  overflow: hidden;
}

.floating-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-bottom: 1px solid #d0d0d0;
  cursor: grab;
  user-select: none;
  flex-shrink: 0;
}

.floating-header:active {
  cursor: grabbing;
}

.floating-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.floating-actions {
  display: flex;
  gap: 6px;
}

.btn-action {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: background-color 0.2s, color 0.2s;
}

.btn-action:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #1a1a1a;
}

.btn-action.btn-close:hover {
  background: #ffebee;
  color: #d32f2f;
}

.floating-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: white;
}

.market-context {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  border-left: 3px solid #1976d2;
}

.market-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
  line-height: 1.4;
  max-height: 2.8em;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.market-url {
  font-size: 11px;
  color: #999;
  word-break: break-all;
}

.floating-minimized {
  position: fixed;
  background: white;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  z-index: 2147483647;
  user-select: none;
  cursor: grab;
}

.floating-minimized:active {
  cursor: grabbing;
}

.floating-minimized-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #1a1a1a;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.floating-resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: se-resize;
  background: linear-gradient(135deg, transparent 0%, #d0d0d0 50%, #d0d0d0 100%);
  border-radius: 0 0 8px 0;
}

.floating-resize-handle:hover {
  background: linear-gradient(135deg, transparent 0%, #1976d2 50%, #1976d2 100%);
}

/* Directional Ideas Styles */
.directional-ideas {
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 20px;
}

.directional-header {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16px;
  padding: 0 12px;
}

.directional-panel {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  transition: background-color 0.2s, border-color 0.2s;
}

.directional-panel.emphasized {
  background: #e8f5e9;
  border-color: #4caf50;
}

.directional-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.directional-panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.directional-panel.emphasized .directional-panel-title {
  color: #2e7d32;
  font-weight: 700;
}

.directional-count {
  font-size: 12px;
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 12px;
  color: #666;
}

.directional-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.directional-item {
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.directional-item-title {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
  line-height: 1.4;
}

.directional-item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.directional-category {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.directional-category.finance {
  background: #e3f2fd;
  color: #1565c0;
}

.directional-category.politics {
  background: #fff3e0;
  color: #e65100;
}

.directional-category.technology {
  background: #f3e5f5;
  color: #6a1b9a;
}

.directional-category.elections {
  background: #fce4ec;
  color: #c2185b;
}

.directional-category.economy {
  background: #e0f2f1;
  color: #00695c;
}

.directional-score {
  font-size: 12px;
  font-weight: 600;
  color: #4caf50;
  background: #e8f5e9;
  padding: 2px 8px;
  border-radius: 4px;
}

.directional-reason {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
  line-height: 1.4;
  font-style: italic;
}

.directional-actions {
  display: flex;
  gap: 8px;
}

.directional-actions button {
  flex: 1;
  padding: 6px 10px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s, color 0.2s;
}

.btn-open {
  background: transparent;
  border: 1px solid #1976d2;
  color: #1976d2;
}

.btn-open:hover {
  background: #e3f2fd;
}

.btn-add {
  background: #1976d2;
  color: white;
}

.btn-add:hover {
  background: #1565c0;
}

/* Scrollbar styling */
.floating-content::-webkit-scrollbar {
  width: 6px;
}

.floating-content::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.floating-content::-webkit-scrollbar-thumb {
  background: #d0d0d0;
  border-radius: 3px;
}

.floating-content::-webkit-scrollbar-thumb:hover {
  background: #999;
}
`;
