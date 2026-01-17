import React from 'react';
import { createRoot } from 'react-dom/client';
import { FloatingAssistant } from '../components/FloatingAssistant';
import type { OverlayState } from '../types';
import { isMarketPage, scrapeCurrentMarket } from '../utils/marketScraper';
import { overlayStore } from '../utils/overlayStore';
import { addToHistory } from '../utils/storage';
import { shadowStyles } from './shadowStyles';

const PANEL_ID = 'pm-overlay-root';
let panelRoot: HTMLElement | null = null;
let reactRoot: any = null;
let floatingButton: HTMLElement | null = null;
let shadowDom: ShadowRoot | null = null;
let isInitialized = false;

function createShadowRoot(): ShadowRoot {
  // Check if already exists
  const existing = document.getElementById(PANEL_ID);
  if (existing && existing.shadowRoot) {
    return existing.shadowRoot;
  }

  // Remove existing if no shadow root
  if (existing) {
    existing.remove();
  }

  const container = document.createElement('div');
  container.id = PANEL_ID;
  container.style.cssText = `
    all: initial;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2147483647;
    pointer-events: none;
  `;
  document.body.appendChild(container);

  const shadowRoot = container.attachShadow({ mode: 'closed' });

  // Inject styles
  const style = document.createElement('style');
  style.textContent = shadowStyles;
  shadowRoot.appendChild(style);

  return shadowRoot;
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
  button.style.cssText = `
    position: fixed;
    bottom: 16px;
    right: 16px;
    z-index: 2147483646;
    padding: 12px 16px;
    background: #1976d2;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    transition: background-color 0.2s, box-shadow 0.2s;
  `;

  button.addEventListener('mouseenter', () => {
    button.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
  });

  button.addEventListener('mouseleave', () => {
    button.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
  });

  button.addEventListener('click', async () => {
    console.debug('[CONTENT] Open panel button clicked');
    try {
      console.debug('[CONTENT] Calling overlayStore.toggleOverlay()');
      await overlayStore.toggleOverlay();
      console.debug('[CONTENT] toggleOverlay() completed successfully');
    } catch (error) {
      console.error('[CONTENT] Error toggling overlay:', error);
    }
  });

  return button;
}

async function renderPanel() {
  if (!isMarketPage()) {
    console.debug('[CONTENT] Not a market page, hiding UI');
    // Not a market page - hide everything
    if (reactRoot && panelRoot) {
      reactRoot.render(null);
    }
    if (floatingButton) {
      floatingButton.style.display = 'none';
    }
    return;
  }

  const state = overlayStore.getState();
  if (!state) {
    console.debug('[CONTENT] No state yet, initializing');
    await overlayStore.init();
  }

  const currentState = overlayStore.getState();
  if (!currentState) {
    console.debug('[CONTENT] Still no state after init, returning');
    return;
  }

  console.debug('[CONTENT] Rendering panel with state:', currentState);

  // Show/hide floating button based on state
  if (floatingButton) {
    floatingButton.style.display = currentState.open ? 'none' : 'block';
    console.debug('[CONTENT] Button display set:', currentState.open ? 'none' : 'block');
  }

  if (!currentState.open) {
    console.debug('[CONTENT] Panel is closed, rendering nothing');
    // Panel is closed - render nothing in shadow DOM
    if (reactRoot && panelRoot) {
      reactRoot.render(null);
    }
    return;
  }

  console.debug('[CONTENT] Panel is open, rendering FloatingAssistant');
  // Panel should be open - render it in shadow DOM
  shadowDom = createShadowRoot();

  // Get or create panel container
  let panelContainer = shadowDom.querySelector('.panel-container-wrapper') as HTMLElement;
  if (!panelContainer) {
    panelContainer = document.createElement('div');
    panelContainer.className = 'panel-container-wrapper';
    panelContainer.style.cssText = `
      all: revert;
      pointer-events: auto;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 2147483647;
    `;
    shadowDom.appendChild(panelContainer);
  }
  panelRoot = panelContainer;

  if (!reactRoot) {
    reactRoot = createRoot(panelContainer);
  }

  const currentMarket = scrapeCurrentMarket();

  // Add to history
  await addToHistory({
    title: currentMarket.title,
    url: currentMarket.url,
    timestamp: Date.now(),
  });

  console.debug('[CONTENT] Rendering FloatingAssistant component');
  reactRoot.render(
    React.createElement(FloatingAssistant, {
      currentMarket,
      state: currentState,
      onStateChange: async (newState: OverlayState) => {
        console.debug('[CONTENT] FloatingAssistant state change:', newState);
        await overlayStore.setState(newState);
        await renderPanel();
      },
    })
  );
}

async function handleStateChange(newState: OverlayState) {
  // Update floating button visibility
  console.debug('[CONTENT] State changed:', newState);
  if (floatingButton) {
    floatingButton.style.display = newState.open ? 'none' : 'block';
    console.debug('[CONTENT] Button visibility set to:', newState.open ? 'hidden' : 'visible');
  }

  // Re-render panel
  await renderPanel();
}

function handleRouteChange() {
  // Debounce route changes
  setTimeout(async () => {
    if (isMarketPage()) {
      await renderPanel();
    } else {
      // Not a market page - hide everything
      if (reactRoot && panelRoot) {
        reactRoot.render(null);
      }
      if (floatingButton) {
        floatingButton.style.display = 'none';
      }
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

  window.addEventListener('popstate', handleRouteChange);
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
    console.debug('[CONTENT] Initial button visibility:', state.open ? 'hidden' : 'visible', 'open=', state.open);
  }

  // Setup SPA detection
  console.debug('[CONTENT] Setting up SPA detection');
  setupSPADetection();

  // Subscribe to state changes
  console.debug('[CONTENT] Subscribing to state changes');
  overlayStore.subscribe(async (newState: OverlayState) => {
    console.debug('[CONTENT] State change subscription triggered');
    await handleStateChange(newState);
  });

  // Initial render
  console.debug('[CONTENT] Initial render');
  await renderPanel();

  isInitialized = true;
  console.debug('[CONTENT] Initialization complete');
}

// Wait for DOM
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
