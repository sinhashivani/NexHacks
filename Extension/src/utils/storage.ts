// Storage module using chrome.storage.sync (MVP - no backend)

import type { BasketLeg, MarketHistoryItem, OverlayState, PinnedOrder } from '../types';

const STORAGE_KEYS = {
  OVERLAY_STATE: 'overlay_state',
  PINNED_ORDERS: 'pinned_orders',
  MARKET_HISTORY: 'market_history',
  BASKET: 'basket',
} as const;

const MAX_HISTORY_ITEMS = 50;
const DEFAULT_PANEL_WIDTH = 380;
const DEFAULT_PANEL_HEIGHT = 720;
const MIN_PANEL_WIDTH = 280;
const MAX_PANEL_WIDTH = 560;
const DEFAULT_X = 16;
const DEFAULT_Y = 16;

// Helper function to check if extension context is valid
function isExtensionContextValid(): boolean {
  try {
    // Check if chrome.runtime.id is accessible
    return chrome?.runtime?.id !== undefined;
  } catch {
    return false;
  }
}

// Overlay State
export async function getOverlayState(): Promise<OverlayState> {
  console.debug('[STORAGE] Getting overlay state');
  
  // Check if extension context is valid
  if (!isExtensionContextValid()) {
    console.warn('[STORAGE] Extension context invalidated - Please reload the page');
    return {
      open: false,
      minimized: false,
      width: DEFAULT_PANEL_WIDTH,
      height: DEFAULT_PANEL_HEIGHT,
      x: window.innerWidth - DEFAULT_PANEL_WIDTH - DEFAULT_X,
      y: window.innerHeight - DEFAULT_PANEL_HEIGHT - DEFAULT_Y,
      layoutMode: 'docked',
    };
  }
  
  try {
    const result = await chrome.storage.sync.get(STORAGE_KEYS.OVERLAY_STATE);
    const state = result[STORAGE_KEYS.OVERLAY_STATE] as OverlayState | undefined;

    if (state) {
      console.debug('[STORAGE] Retrieved saved state:', state);
      return state;
    } else {
      const defaultState: OverlayState = {
        open: false,
        minimized: false,
        width: DEFAULT_PANEL_WIDTH,
        height: DEFAULT_PANEL_HEIGHT,
        x: window.innerWidth - DEFAULT_PANEL_WIDTH - DEFAULT_X,
        y: window.innerHeight - DEFAULT_PANEL_HEIGHT - DEFAULT_Y,
        layoutMode: 'docked',
      };
      console.debug('[STORAGE] No saved state, returning default:', defaultState);
      return defaultState;
    }
  } catch (error) {
    console.error('[STORAGE] Error getting overlay state:', error);
    return {
      open: false,
      minimized: false,
      width: DEFAULT_PANEL_WIDTH,
      height: DEFAULT_PANEL_HEIGHT,
      x: window.innerWidth - DEFAULT_PANEL_WIDTH - DEFAULT_X,
      y: window.innerHeight - DEFAULT_PANEL_HEIGHT - DEFAULT_Y,
      layoutMode: 'docked',
    };
  }
}

export async function saveOverlayState(state: OverlayState): Promise<void> {
  console.debug('[STORAGE] Saving overlay state:', state);
  
  if (!isExtensionContextValid()) {
    console.warn('[STORAGE] Extension context invalidated - Cannot save state. Please reload the page.');
    return;
  }
  
  try {
    await chrome.storage.sync.set({ [STORAGE_KEYS.OVERLAY_STATE]: state });
    console.debug('[STORAGE] State saved successfully');
  } catch (error) {
    console.error('[STORAGE] Error saving overlay state:', error);
  }
}

// Pinned Orders
export async function getPinnedOrders(): Promise<PinnedOrder[]> {
  const result = await chrome.storage.sync.get(STORAGE_KEYS.PINNED_ORDERS);
  return (result[STORAGE_KEYS.PINNED_ORDERS] as PinnedOrder[]) || [];
}

export async function savePinnedOrder(order: PinnedOrder): Promise<void> {
  if (!isExtensionContextValid()) {
    console.warn('[STORAGE] Extension context invalidated');
    return;
  }
  
  const orders = await getPinnedOrders();
  orders.push(order);
  await chrome.storage.sync.set({ [STORAGE_KEYS.PINNED_ORDERS]: orders });
}

export async function removePinnedOrder(id: string): Promise<void> {
  const orders = await getPinnedOrders();
  const filtered = orders.filter(o => o.id !== id);
  await chrome.storage.sync.set({ [STORAGE_KEYS.PINNED_ORDERS]: filtered });
}

export async function reorderPinnedOrder(id: string, direction: 'up' | 'down'): Promise<void> {
  if (!isExtensionContextValid()) {
    console.warn('[STORAGE] Extension context invalidated');
    return;
  }
  
  const orders = await getPinnedOrders();
  const index = orders.findIndex(o => o.id === id);

  if (index === -1) return;

  if (direction === 'up' && index > 0) {
    [orders[index - 1], orders[index]] = [orders[index], orders[index - 1]];
  } else if (direction === 'down' && index < orders.length - 1) {
    [orders[index], orders[index + 1]] = [orders[index + 1], orders[index]];
  }

  await chrome.storage.sync.set({ [STORAGE_KEYS.PINNED_ORDERS]: orders });
}

// Market History
export async function addToHistory(item: MarketHistoryItem): Promise<void> {
  const history = await getMarketHistory();

  // Remove duplicate if exists (same URL)
  const filtered = history.filter(h => h.url !== item.url);

  // Add to front
  filtered.unshift(item);

  // Keep last 50
  const trimmed = filtered.slice(0, MAX_HISTORY_ITEMS);

  await chrome.storage.sync.set({ [STORAGE_KEYS.MARKET_HISTORY]: trimmed });
}

export async function getMarketHistory(): Promise<MarketHistoryItem[]> {
  const result = await chrome.storage.sync.get(STORAGE_KEYS.MARKET_HISTORY);
  return (result[STORAGE_KEYS.MARKET_HISTORY] as MarketHistoryItem[]) || [];
}

// Basket
export async function getBasket(): Promise<BasketLeg[]> {
  if (!isExtensionContextValid()) {
    console.warn('[STORAGE] Extension context invalidated');
    return [];
  }
  
  try {
    const result = await chrome.storage.sync.get(STORAGE_KEYS.BASKET);
    return (result[STORAGE_KEYS.BASKET] as BasketLeg[]) || [];
  } catch (error) {
    console.error('[STORAGE] Error getting basket:', error);
    return [];
  }
}

export async function saveBasket(basket: BasketLeg[]): Promise<void> {
  if (!isExtensionContextValid()) {
    console.warn('[STORAGE] Extension context invalidated');
    return;
  }
  
  await chrome.storage.sync.set({ [STORAGE_KEYS.BASKET]: basket });
}

// Constants
export const PANEL_CONSTANTS = {
  MIN_WIDTH: MIN_PANEL_WIDTH,
  MAX_WIDTH: MAX_PANEL_WIDTH,
  DEFAULT_WIDTH: DEFAULT_PANEL_WIDTH,
  DEFAULT_HEIGHT: DEFAULT_PANEL_HEIGHT,
  DEFAULT_X,
  DEFAULT_Y,
};
