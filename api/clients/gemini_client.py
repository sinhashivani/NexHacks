"""Google Gemini AI Client for smart recommendations."""

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from typing import List, Dict, Any, Optional
import os
import numpy as np

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client with API key from env or parameter"""
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if genai is None or not api_key:
            print("⚠️  Gemini AI not available (missing google-generativeai or API key)")
            self.model = None
            self.embedding_model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            # Use text-embedding-004 for embeddings
            self.embedding_model = 'models/text-embedding-004'
            print("✅ Gemini AI client initialized successfully")
        except Exception as e:
            print(f"⚠️  Gemini client initialization failed: {e}")
            self.model = None
            self.embedding_model = None
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using Gemini's embedding model"""
        if not self.embedding_model:
            return None
        
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"  # or "retrieval_query" for queries
            )
            embedding = result['embedding']
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def get_query_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a query (optimized for search)"""
        if not self.embedding_model:
            return None
        
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            embedding = result['embedding']
            return embedding
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return None
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities and keywords from text using Gemini"""
        if not self.model:
            # Fallback: simple keyword extraction
            return {
                "entities": [],
                "keywords": text.lower().split()[:10],
                "topics": []
            }
        
        try:
            prompt = f"""Extract key entities, topics, and keywords from the following market title or description. 
Return a JSON object with:
- entities: list of named entities (people, organizations, events)
- keywords: list of important keywords
- topics: list of topic categories (Politics, Finance, Technology, Sports, etc.)

Text: {text}

Return only valid JSON."""
            
            response = self.model.generate_content(prompt)
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response.text.strip())
                return result
            except:
                # Fallback
                return {
                    "entities": [],
                    "keywords": text.lower().split()[:10],
                    "topics": []
                }
        except Exception as e:
            print(f"Error extracting entities with Gemini: {e}")
            return {
                "entities": [],
                "keywords": text.lower().split()[:10],
                "topics": []
            }
    
    def compute_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts"""
        if not self.model:
            # Fallback: simple word overlap (Jaccard similarity)
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0.0
        
        try:
            prompt = f"""Rate the semantic similarity between these two market titles on a scale of 0 to 1.
Consider:
- Topic similarity
- Related events or entities
- Potential market correlation
- Similar outcomes or predictions

Title 1: {text1}
Title 2: {text2}

Return only a single number between 0 and 1 (e.g., 0.75)"""
            
            response = self.model.generate_content(prompt)
            # Parse numeric response
            try:
                score = float(response.text.strip())
                return max(0.0, min(1.0, score))
            except:
                # Fallback if parsing fails
                words1 = set(text1.lower().split())
                words2 = set(text2.lower().split())
                if not words1 or not words2:
                    return 0.0
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                return len(intersection) / len(union) if union else 0.0
        except Exception as e:
            print(f"Error computing similarity with Gemini: {e}")
            # Fallback
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0.0
    
    async def rank_recommendations(
        self,
        primary_market: str,
        candidate_markets: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Use AI to rank and filter candidate markets for recommendations"""
        if not self.model or not candidate_markets:
            # Return top candidates by similarity if available
            return sorted(
                candidate_markets,
                key=lambda x: x.get("cosine_similarity", 0),
                reverse=True
            )[:limit]
        
        try:
            # Create a prompt with candidate titles
            candidate_titles = [f"{i+1}. {m.get('question', 'Unknown')}" for i, m in enumerate(candidate_markets[:20])]
            candidates_text = "\n".join(candidate_titles)
            
            prompt = f"""Given this primary market:
"{primary_market}"

Rank these candidate markets by relevance for a trader interested in the primary market.
Consider: correlation potential, topic similarity, related events, hedge opportunities.

Candidates:
{candidates_text}

Return the top {min(limit, len(candidate_markets))} most relevant market numbers (e.g., "1,3,7,...")"""
            
            response = self.model.generate_content(prompt)
            # Parse the response to get ranked indices
            ranked_indices = []
            for part in response.text.strip().split(','):
                try:
                    idx = int(part.strip()) - 1
                    if 0 <= idx < len(candidate_markets):
                        ranked_indices.append(idx)
                except:
                    continue
            
            # Return ranked markets
            result = [candidate_markets[i] for i in ranked_indices if i < len(candidate_markets)]
            
            # Fill remaining spots with unranked candidates
            unranked = [m for i, m in enumerate(candidate_markets) if i not in ranked_indices]
            result.extend(unranked)
            
            return result[:limit]
            
        except Exception as e:
            print(f"Error ranking with Gemini: {e}")
            # Fallback to similarity-based ranking
            return sorted(
                candidate_markets,
                key=lambda x: x.get("cosine_similarity", 0),
                reverse=True
            )[:limit]
