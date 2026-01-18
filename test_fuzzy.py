#!/usr/bin/env python3
"""Test fuzzy matching endpoint"""

import requests

url = "http://localhost:8000/similar?event_title=Supreme%20Court"
response = requests.get(url)
data = response.json()

print(f"Event title searched: {data['event_title']}")
print(f"Similar markets found: {len(data.get('similar_markets', []))}")
print("\nFirst 3 matches:")
for market in data.get('similar_markets', [])[:3]:
    print(f"  - {market['question']}")
