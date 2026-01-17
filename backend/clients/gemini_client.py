import google.generativeai as genai
from typing import List, Dict, Any, Optional
from config import settings

class GeminiClient:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities and keywords from text using Gemini"""
        if not self.model:
            # Fallback: simple keyword extraction
            return {
                "entities": [],
                "keywords": text.lower().split()[:10],
            }
        
        try:
            prompt = f"""Extract key entities, topics, and keywords from the following market title or description. 
Return a JSON object with:
- entities: list of named entities (people, organizations, events)
- keywords: list of important keywords
- topics: list of topic categories

Text: {text}

Return only valid JSON."""
            
            response = self.model.generate_content(prompt)
            # Parse response (may need adjustment based on actual Gemini response format)
            # For now, return a simple structure
            return {
                "entities": [],
                "keywords": text.lower().split()[:10],
                "topics": [],
            }
        except Exception as e:
            print(f"Error extracting entities with Gemini: {e}")
            return {
                "entities": [],
                "keywords": text.lower().split()[:10],
            }
    
    def compute_semantic_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts"""
        if not self.model:
            # Fallback: simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0.0
        
        try:
            prompt = f"""Rate the semantic similarity between these two market titles on a scale of 0 to 1.
Return only a number between 0 and 1.

Title 1: {text1}
Title 2: {text2}

Similarity score:"""
            
            response = self.model.generate_content(prompt)
            # Parse numeric response
            try:
                score = float(response.text.strip())
                return max(0.0, min(1.0, score))
            except:
                return 0.5
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
