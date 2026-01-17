import type { RecommendationRequest, RecommendationResponse, TagsResponse } from '../types';

const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND || import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export async function getRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  const response = await fetch(`${BACKEND_BASE_URL}/v1/recommendations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getTags(): Promise<TagsResponse> {
  const response = await fetch(`${BACKEND_BASE_URL}/v1/tags`);
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}
