// MVP Types - No backend dependencies

export interface PinnedOrder {
  id: string;
  title: string;
  url: string;
  timestamp: number;
  side?: 'YES' | 'NO';
  amount?: number;
  notes: string;
}

export interface MarketHistoryItem {
  title: string;
  url: string;
  timestamp: number;
}

export interface MarketRecommendation {
  id: string;
  title: string;
  url: string;
  category: 'Finance' | 'Politics' | 'Technology' | 'Elections' | 'Economy';
  score: number;
  reason: string;
}

export interface BasketLeg {
  id: string;
  title: string;
  url: string;
  category?: string;
  visited: boolean;
}

export interface OverlayState {
  open: boolean;
  minimized: boolean;
  width: number;
  height: number;
  x: number;
  y: number;
}

export interface StorageData {
  overlay_state: OverlayState;
  pinned_orders: PinnedOrder[];
  market_history: MarketHistoryItem[];
  basket: BasketLeg[];
}

export interface CurrentMarket {
  title: string;
  url: string;
  side?: 'YES' | 'NO';
  amount?: number;
}
