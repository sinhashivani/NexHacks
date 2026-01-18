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
  layoutMode: 'docked' | 'floating';
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

// API Request/Response Types
export interface LocalProfile {
  recent_interactions: Array<{
    title: string;
    url: string;
    timestamp: number;
    side?: 'YES' | 'NO';
  }>;
  topic_counts: Record<string, number>;
  entity_counts: Record<string, number>;
}

export interface RecommendationRequest {
  primary: {
    url: string;
    side?: 'YES' | 'NO';
    amount?: number;
    trigger_type?: string;
  };
  local_profile: LocalProfile;
}

export interface RecommendationResponse {
  amplify: MarketRecommendation[];
  hedge: MarketRecommendation[];
}

export interface TagsResponse {
  tags: string[];
}
