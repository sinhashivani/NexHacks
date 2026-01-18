import React from 'react';
import { createRoot, Root } from 'react-dom/client';
import { FloatingAssistant } from '../components/FloatingAssistant';
import type { OverlayState } from '../types';
import { isMarketPage, scrapeCurrentMarket } from '../utils/marketScraper';
import { overlayStore } from '../utils/overlayStore';
import { addToHistory } from '../utils/storage';
import { shadowStyles } from './shadowStyles';

// Module-scope singletons
let shadowHost: HTMLElement | null = null;
let shadowRoot: ShadowRoot | null = null;
let panelEl: HTMLElement | null = null;
let reactRoot: Root | null = null;
let floatingButton: HTMLElement | null = null;

// Trade observer
let mutationObserver: MutationObserver | null = null;
let isInitialized = false;

/**
 * Apply or remove page push for docked mode
 */
function applyPagePush(state: OverlayState): void {
  if (state.layoutMode === 'docked' && state.open) {
    console.debug('[CONTENT] Applying page push:', state.width + 24);
    document.documentElement.style.paddingRight = `${state.width + 24}px`;
  } else {
    console.debug('[CONTENT] Removing page push');
    document.documentElement.style.paddingRight = '';
  }
}

/**
 * Create shadow host and root ONCE - never recreate
 */
function ensureUiOnce(): void {
  if (reactRoot) {
    console.debug('[CONTENT] UI already initialized, reusing');
    return;
  }

  console.debug('[CONTENT] Creating shadow DOM structure');

  // Create shadow host
  shadowHost = document.createElement('div');
  shadowHost.id = 'pm-overlay-host';
  shadowHost.style.position = 'fixed';
  shadowHost.style.inset = '0';
  shadowHost.style.pointerEvents = 'none'; // CRITICAL: do not block page clicks
  shadowHost.style.zIndex = '2147483647';

  // Attach shadow root
  shadowRoot = shadowHost.attachShadow({ mode: 'open' });

  // Inject styles into shadow root
  const style = document.createElement('style');
  style.textContent = shadowStyles;
  shadowRoot.appendChild(style);

  // Create panel element (child of shadow root)
  panelEl = document.createElement('div');
  panelEl.id = 'pm-overlay-panel';
  panelEl.style.position = 'fixed';
  panelEl.style.pointerEvents = 'auto'; // Panel CAN receive clicks
  panelEl.style.display = 'none'; // Start hidden
  shadowRoot.appendChild(panelEl);

  // Append shadow host to document
  document.documentElement.appendChild(shadowHost);

  // Create React root in panel element
  reactRoot = createRoot(panelEl);

  console.debug('[CONTENT] Shadow DOM structure created');
}

/**
 * Update panel positioning based on layout mode
 */
function updatePanelPosition(state: OverlayState): void {
  if (!panelEl) return;

  if (state.layoutMode === 'docked') {
    // Docked mode: fixed on right
    panelEl.style.right = '16px';
    panelEl.style.top = '16px';
    panelEl.style.bottom = '16px';
    panelEl.style.left = 'auto';
    panelEl.style.width = `${state.width}px`;
    panelEl.style.height = 'auto';
  } else {
    // Floating mode: absolute positioning from x/y
    panelEl.style.left = `${state.x}px`;
    panelEl.style.top = `${state.y}px`;
    panelEl.style.right = 'auto';
    panelEl.style.bottom = 'auto';
    panelEl.style.width = `${state.width}px`;
    panelEl.style.height = `${state.height}px`;
  }
}

/**
 * Render UI - call only this, never recreate shadow root
 */
function render(state: OverlayState): void {
  ensureUiOnce();

  if (!panelEl || !reactRoot) {
    console.error('[CONTENT] Panel or React root not initialized');
    return;
  }

  // Update panel display and position
  panelEl.style.display = state.open ? 'block' : 'none';
  updatePanelPosition(state);

  // Apply or remove page push
  applyPagePush(state);

  if (state.open) {
    const currentMarket = scrapeCurrentMarket();

    // Render component
    console.debug('[CONTENT] Rendering FloatingAssistant');
    reactRoot.render(
      React.createElement(FloatingAssistant, {
        currentMarket,
        state,
        onStateChange: (newState: Partial<OverlayState>) => {
          console.debug('[CONTENT] FloatingAssistant state change:', newState);
          overlayStore.setState(newState);
        },
      })
    );

    startTradeObserver();
  } else {
    stopTradeObserver();
  }
}

function createFloatingButton(): HTMLElement {
  // Check if already exists
  const existing = document.getElementById('pm-floating-button');
  if (existing) {
    return existing as HTMLElement;
  }

  const button = document.createElement('button');
  button.id = 'pm-floating-button';
  button.textContent = 'Open panel';
  
  // Initial position (will be saved/restored from storage)
  let buttonX = window.innerWidth - 120;
  let buttonY = window.innerHeight - 60;
  
  const updateButtonPosition = () => {
    button.style.left = `${buttonX}px`;
    button.style.top = `${buttonY}px`;
  };
  
  button.style.cssText = `
    display: block;
    width: auto;
    height: auto;
    position: fixed;
    z-index: 2147483646;
    padding: 12px 16px;
    background: #1a1a1a;
    color: #4a90ff;
    border: 1px solid #404040;
    border-radius: 8px;
    cursor: grab;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px #000000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    transition: background-color 0.2s, box-shadow 0.2s, border-color 0.2s;
    user-select: none;
    pointer-events: auto;
  `;
  
  updateButtonPosition();

  // Drag functionality
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let hasMoved = false;

  button.addEventListener('pointerdown', (e) => {
    isDragging = true;
    hasMoved = false;
    dragStartX = e.clientX - buttonX;
    dragStartY = e.clientY - buttonY;
    button.style.cursor = 'grabbing';
    button.setPointerCapture(e.pointerId);
    e.preventDefault();
  });

  document.addEventListener('pointermove', (e) => {
    if (!isDragging) return;
    
    hasMoved = true;
    buttonX = e.clientX - dragStartX;
    buttonY = e.clientY - dragStartY;
    
    // Keep button within viewport bounds
    buttonX = Math.max(0, Math.min(buttonX, window.innerWidth - button.offsetWidth));
    buttonY = Math.max(0, Math.min(buttonY, window.innerHeight - button.offsetHeight));
    
    updateButtonPosition();
  }, { passive: true });

  document.addEventListener('pointerup', (e) => {
    if (!isDragging) return;
    
    isDragging = false;
    button.style.cursor = 'grab';
    
    try {
      button.releasePointerCapture(e.pointerId);
    } catch (_) {
      // Ignore errors
    }
    
    // Only open if not dragged (click vs drag detection)
    if (!hasMoved) {
      e.stopPropagation();
      console.debug('[CONTENT] Open panel button clicked');
      try {
        const state = overlayStore.getState();
        if (state) {
          overlayStore.setOpen(!state.open);
        }
      } catch (error) {
        console.error('[CONTENT] Error toggling overlay:', error);
      }
    }
    
    hasMoved = false;
  }, { passive: true });

  button.addEventListener('mouseenter', () => {
    if (!isDragging) {
      button.style.boxShadow = '0 6px 16px #000000';
      button.style.borderColor = '#4a90ff';
      button.style.background = '#252525';
    }
  }, { passive: true });

  button.addEventListener('mouseleave', () => {
    if (!isDragging) {
      button.style.boxShadow = '0 4px 12px #000000';
      button.style.borderColor = '#404040';
      button.style.background = '#1a1a1a';
    }
  }, { passive: true });

  return button;
}

function startTradeObserver() {
  if (mutationObserver) {
    console.debug('[CONTENT] Trade observer already running');
    return;
  }

  console.debug('[CONTENT] Starting trade data observer');

  // Look for trade table or order book DOM
  const tradeTarget = document.querySelector('[data-testid*="order"], [class*="trade"], [class*="market-card"]');
  if (!tradeTarget) {
    console.debug('[CONTENT] No trade DOM found to observe');
    return;
  }

  mutationObserver = new MutationObserver((mutations) => {
    // Extract trade data from mutations
    mutations.forEach((mutation) => {
      const target = mutation.target as HTMLElement;

      // Look for price, volume, or trade data in text content
      const priceMatch = target.textContent?.match(/[\$]?([\d,]+\.?\d*)/);
      const volumeMatch = target.textContent?.match(/vol[ume]*:?\s*[\d,]+/i);

      if (priceMatch || volumeMatch) {
        console.debug('[CONTENT] Trade data mutation detected:', {
          price: priceMatch?.[1],
          volume: volumeMatch?.[0],
          element: target.tagName,
        });
      }
    });
  });

  mutationObserver.observe(tradeTarget, {
    subtree: true,
    characterData: true,
    childList: true,
    attributes: true,
  });

  console.debug('[CONTENT] Trade observer started');
}

function stopTradeObserver() {
  if (mutationObserver) {
    console.debug('[CONTENT] Stopping trade data observer');
    mutationObserver.disconnect();
    mutationObserver = null;
  }
}

function handleRouteChange() {
  // Debounce route changes
  setTimeout(async () => {
    if (isMarketPage()) {
      console.debug('[CONTENT] Route changed to market page, updating UI');
      const state = overlayStore.getState();
      if (state) {
        render(state);
      }
    } else {
      console.debug('[CONTENT] Route changed to non-market page, hiding UI');
      if (floatingButton) {
        floatingButton.style.display = 'none';
      }
      stopTradeObserver();
    }
  }, 100);
}

function setupSPADetection() {
  // Watch for route changes
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;

  history.pushState = function (...args) {
    originalPushState.apply(history, args);
    handleRouteChange();
  };

  history.replaceState = function (...args) {
    originalReplaceState.apply(history, args);
    handleRouteChange();
  };

  // Passive: popstate listeners don't need preventDefault()
  window.addEventListener('popstate', handleRouteChange, { passive: true });
}

async function init() {
  if (isInitialized) {
    console.debug('[CONTENT] Already initialized, skipping');
    return;
  }

  console.debug('[CONTENT] Initializing extension');

  // Initialize store
  console.debug('[CONTENT] Initializing overlayStore');
  await overlayStore.init();
  console.debug('[CONTENT] overlayStore initialized');

  // Create floating button
  const existingButton = document.getElementById('pm-floating-button');
  if (existingButton) {
    console.debug('[CONTENT] Removing existing button');
    existingButton.remove();
  }

  console.debug('[CONTENT] Creating floating button');
  floatingButton = createFloatingButton();
  document.body.appendChild(floatingButton);
  console.debug('[CONTENT] Floating button created and appended');

  // Set initial visibility based on state
  const state = overlayStore.getState();
  if (floatingButton && state) {
    floatingButton.style.display = state.open ? 'none' : 'block';
    console.debug('[CONTENT] Initial button visibility:', state.open ? 'hidden' : 'visible');
  }

  // Setup SPA detection
  console.debug('[CONTENT] Setting up SPA detection');
  setupSPADetection();

  // Ensure UI is created ONCE
  console.debug('[CONTENT] Ensuring UI created once');
  ensureUiOnce();

  // Subscribe to state changes - only update, never recreate
  console.debug('[CONTENT] Subscribing to state changes');
  overlayStore.subscribe(async (newState: OverlayState) => {
    console.debug('[CONTENT] State change subscription triggered');
    render(newState);

    // Update button visibility
    if (floatingButton) {
      floatingButton.style.display = newState.open ? 'none' : 'block';
    }

    // Add to history if opening
    if (newState.open && isMarketPage()) {
      const currentMarket = scrapeCurrentMarket();
      await addToHistory({
        title: currentMarket.title,
        url: currentMarket.url,
        timestamp: Date.now(),
      });
    }
  });

  // Clean up on page unload
  window.addEventListener('beforeunload', () => {
    console.debug('[CONTENT] Page unload, cleaning up');
    stopTradeObserver();
  });

  // Initial render
  console.debug('[CONTENT] Initial render');
  if (state) {
    render(state);
  }

  isInitialized = true;
  console.debug('[CONTENT] Initialization complete');
}

// Wait for DOM
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
