#!/usr/bin/env python3
"""Find the Supreme Court market"""

from database.supabase_connection import SupabaseConnection

conn = SupabaseConnection()
client = conn.get_client()

# Search for Supreme Court market
search_terms = [
    "Supreme Court",
    "Trump",
    "tariff"
]

for term in search_terms:
    result = client.table('markets').select('question, market_id, market_slug').ilike('question', f'%{term}%').limit(5).execute()
    print(f'\nMarkets matching "{term}": {len(result.data)}')
    for r in result.data[:3]:
        print(f'  - {r["question"]}')

# Try exact match
print('\n' + '='*60)
print('Testing what the extension would scrape:')
print('='*60)

test_questions = [
    "Will the Supreme Court rule on Trump's tariffs by January 31?",
    "Supreme Court rules in favor of Trump",
    "Will Trump acquire Greenland before 2027?"
]

for q in test_questions:
    result = client.table('markets').select('question, market_id').eq('question', q).execute()
    if result.data:
        print(f'\nFOUND exact match: {q}')
        print(f'  Market ID: {result.data[0]["market_id"]}')
    else:
        print(f'\nNOT FOUND: {q}')
        # Try fuzzy match
        fuzzy = client.table('markets').select('question').ilike('question', f'%{q.split()[0]}%').limit(3).execute()
        if fuzzy.data:
            print(f'  Similar markets:')
            for f in fuzzy.data:
                print(f'    - {f["question"]}')
