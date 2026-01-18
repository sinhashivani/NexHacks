import type { RecommendationRequest, RecommendationResponse, TagsResponse } from '../types';

const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND || import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// FLAG #1: BACKEND URL ASSUMPTION
// ASSUMPTION: Backend runs on http://localhost:8000 or env var VITE_BACKEND/VITE_BACKEND_URL
// TEST NEEDED: Verify actual backend URL in deployment
// ACTUAL URL: {BACKEND_BASE_URL}
console.log('[API] Backend URL:', BACKEND_BASE_URL);

// FLAG #2: API TIMEOUT ASSUMPTION
// ASSUMPTION: 5 second timeout is reasonable for API response
// TEST NEEDED: Adjust if actual API response times differ
const API_TIMEOUT_MS = 5000;

export async function getRecommendations(
  request: RecommendationRequest,
  options: { timeout?: number } = {}
): Promise<RecommendationResponse> {
  const timeoutMs = options.timeout || API_TIMEOUT_MS;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    console.log('[API] Fetching recommendations:', {
      primary: request.primary,
      interactionCount: request.local_profile.recent_interactions.length,
      topicCount: Object.keys(request.local_profile.topic_counts).length,
    });

    const response = await fetch(`${BACKEND_BASE_URL}/v1/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // FLAG #3: ERROR HANDLING ASSUMPTION
    // ASSUMPTION: Non-200 responses should throw, caller handles gracefully
    // TEST NEEDED: Verify backend returns expected status codes
    if (!response.ok) {
      const errorText = await response.text().catch(() => response.statusText);
      console.error('[API] Error response:', response.status, errorText);
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('[API] Recommendations received:', {
      amplifyCount: data.amplify?.length || 0,
      hedgeCount: data.hedge?.length || 0,
    });

    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error('[API] Request timeout after', timeoutMs, 'ms');
      } else {
        console.error('[API] Fetch error:', error.message);
      }
    } else {
      console.error('[API] Unknown error:', error);
    }

    // FLAG #3: SILENT FAILURE ASSUMPTION
    // ASSUMPTION: Errors throw, parent handles gracefully
    // TEST NEEDED: Verify parent component catches and handles
    throw error;
  }
}

export async function getTags(): Promise<TagsResponse> {
  const response = await fetch(`${BACKEND_BASE_URL}/v1/tags`);

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function getTrendingMarkets(category?: string, limit: number = 20): Promise<any> {
  try {
    const params = new URLSearchParams();
    if (category && category !== 'all') params.append('category', category);
    params.append('limit', limit.toString());
    
    const url = `${BACKEND_BASE_URL}/markets/trending?${params}`;
    console.log('[API] Fetching trending markets:', url);
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e952f87d-c0d8-4db6-a4a0-05d7096a8080',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:94',message:'About to fetch trending markets',data:{url,method:'GET'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    
    const response = await fetch(url).catch((error) => {
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/e952f87d-c0d8-4db6-a4a0-05d7096a8080',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:97',message:'Fetch error caught',data:{error:error.message,errorType:error.constructor.name,url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      throw error;
    });
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e952f87d-c0d8-4db6-a4a0-05d7096a8080',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:102',message:'Fetch response received',data:{status:response.status,statusText:response.statusText,ok:response.ok,headers:Object.fromEntries(response.headers.entries())},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('[API] Trending markets received:', data.count);
    return data;
  } catch (error) {
    console.error('[API] Error fetching trending markets:', error);
    throw error;
  }
}

export async function getSimilarMarkets(
  eventTitle: string, 
  useCosine: boolean = true,
  minSimilarity: number = 0.5
): Promise<any> {
  try {
    const params = new URLSearchParams({ 
      event_title: eventTitle,
      use_cosine: useCosine.toString(),
      min_similarity: minSimilarity.toString()
    });
    const url = `${BACKEND_BASE_URL}/similar?${params}`;
    
    console.log('[API] ========================================');
    console.log('[API] FETCHING SIMILAR MARKETS');
    console.log('[API] ========================================');
    console.log('[API] Event title:', eventTitle);
    console.log('[API] Use cosine similarity:', useCosine);
    console.log('[API] Min similarity threshold:', minSimilarity);
    console.log('[API] Full URL:', url);
    console.log('[API] ========================================');
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e952f87d-c0d8-4db6-a4a0-05d7096a8080',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:133',message:'About to fetch similar markets',data:{url,method:'GET'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    
    const startTime = performance.now();
    const response = await fetch(url).catch((error) => {
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/e952f87d-c0d8-4db6-a4a0-05d7096a8080',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:135',message:'Fetch error caught',data:{error:error.message,errorType:error.constructor.name,url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      throw error;
    });
    const endTime = performance.now();
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e952f87d-c0d8-4db6-a4a0-05d7096a8080',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:140',message:'Fetch response received',data:{status:response.status,statusText:response.statusText,ok:response.ok,headers:Object.fromEntries(response.headers.entries())},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    
    console.log(`[API] Request took ${(endTime - startTime).toFixed(2)}ms`);
    
    if (!response.ok) {
      console.error('[API] HTTP Error:', response.status, response.statusText);
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    console.log('[API] ========================================');
    console.log('[API] SIMILAR MARKETS RESPONSE');
    console.log('[API] ========================================');
    console.log('[API] Total markets found:', data.count || data.similar_markets?.length || 0);
    console.log('[API] Strategy used:', data.strategy_used || 'unknown');
    
    if (data.similar_markets && data.similar_markets.length > 0) {
      console.log('[API] Top 5 similar markets:');
      data.similar_markets.slice(0, 5).forEach((market: any, idx: number) => {
        console.log(`[API]   #${idx + 1}: ${market.question.substring(0, 60)}...`);
        console.log(`[API]       Cosine similarity: ${market.cosine_similarity?.toFixed(4) || 'N/A'}`);
        console.log(`[API]       Match type: ${market.match_type || 'unknown'}`);
      });
    } else {
      console.warn('[API] No similar markets found');
    }
    
    console.log('[API] ========================================');
    
    return data;
  } catch (error) {
    console.error('[API] ========================================');
    console.error('[API] ERROR FETCHING SIMILAR MARKETS');
    console.error('[API] ========================================');
    console.error('[API] Error:', error);
    console.error('[API] Event title was:', eventTitle);
    console.error('[API] ========================================');
    throw error;
  }
}

export interface NewsArticle {
  title: string;
  image?: string;
  name: string;
}

export interface NewsResponse {
  question: string;
  count: number;
  articles: NewsArticle[];
}

export const getNews = async (question: string): Promise<NewsResponse> => {
  console.log('[API] Fetching news:', `${API_BASE_URL}/news?question=${encodeURIComponent(question)}`);
  
  try {
    const response = await fetch(
      `${API_BASE_URL}/news?question=${encodeURIComponent(question)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('[API] News response:', data);
    return data;
  } catch (error) {
    console.error('[API] Error fetching news:', error);
    throw error;
  }
}

export async function getRelatedMarkets(marketId?: string, eventTitle?: string, limit: number = 10): Promise<any> {
  try {
    const params = new URLSearchParams();
    if (marketId) params.append('market_id', marketId);
    if (eventTitle) params.append('event_title', eventTitle);
    params.append('limit', limit.toString());
    
    const url = `${BACKEND_BASE_URL}/related?${params}`;
    console.log('[API] Fetching related markets:', url);
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('[API] Related markets received:', data.count);
    return data;
  } catch (error) {
    console.error('[API] Error fetching related markets:', error);
    throw error;
  }
}
