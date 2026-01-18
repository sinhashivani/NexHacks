#!/usr/bin/env python3
"""Test cosine similarity endpoint with logging"""

import requests

# Test with a market that exists
url = "http://localhost:8000/similar?event_title=Supreme%20Court%20rules%20in%20favor%20of%20Trump%27s%20tariffs&use_cosine=true&min_similarity=0.5"

print("Testing cosine similarity endpoint...")
print(f"URL: {url}\n")

response = requests.get(url)
data = response.json()

print(f"Event title: {data.get('event_title')}")
print(f"Total markets found: {data.get('count', 0)}")
print(f"Strategy used: {data.get('strategy_used', 'unknown')}\n")

if data.get('similar_markets'):
    print("Similar markets:")
    for idx, market in enumerate(data['similar_markets'][:5], 1):
        print(f"\n#{idx}:")
        print(f"  Question: {market['question']}")
        print(f"  Cosine similarity: {market.get('cosine_similarity', 'N/A')}")
        print(f"  Match type: {market.get('match_type', 'unknown')}")
else:
    print("No similar markets found")
