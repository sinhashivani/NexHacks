#!/usr/bin/env python3
"""Check database contents"""

from database.supabase_connection import SupabaseConnection

conn = SupabaseConnection()
client = conn.get_client()

print('Checking both tables...\n')

# Check markets table (from schema.sql)
try:
    result = client.table('markets').select('question, market_id, market_slug', count='exact').limit(10).execute()
    print(f'MARKETS table: {result.count} rows')
    if result.data:
        print('Sample questions:')
        for r in result.data[:3]:
            print(f'  - {r["question"]}')
except Exception as e:
    print(f'MARKETS table error: {e}')

print()

# Check market_metrics table (from migration 003)
try:
    result2 = client.table('market_metrics').select('*', count='exact').limit(1).execute()
    print(f'MARKET_METRICS table: {result2.count} rows')
    if result2.data:
        print('Columns:', list(result2.data[0].keys()))
        print('Sample row:', result2.data[0])
except Exception as e:
    print(f'MARKET_METRICS table error: {e}')

print('\n' + '='*60)
print('DIAGNOSIS:')
print('='*60)
print('Need to check which table has your Polymarket data!')
print('='*60)
