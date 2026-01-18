"""Quick script to check if CSV data matches database"""
import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.supabase_connection import SupabaseConnection

print("=" * 60)
print("Checking Data Match Between CSV and Database")
print("=" * 60)

# Get database sample
conn = SupabaseConnection()
client = conn.get_client()

print("\n1. Database Markets Sample:")
db_markets = client.table("markets").select("clob_token_ids, question").limit(5).execute()
db_token_set = set()
for i, m in enumerate(db_markets.data, 1):
    tokens = m.get("clob_token_ids", "")
    question = m.get("question", "")[:50]
    print(f"   {i}. {question}...")
    print(f"      tokens: {tokens[:80]}...")
    db_token_set.add(tokens)

# Get total count
total = client.table("markets").select("market_id", count="exact").execute()
print(f"\n   Total markets in database: {total.count}")

# Get CSV sample
print("\n2. CSV Data Sample:")
csv_path = "data/polymarket_events_by_tags.csv"
csv_tokens = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, quotechar='"', skipinitialspace=True)
    header = next(reader)
    header = [col.strip() for col in header]
    print(f"   Columns: {header}")
    
    clob_idx = header.index('clob_token_ids')
    event_idx = header.index('event_title')
    
    for i, row in enumerate(reader):
        if i >= 5:
            break
        event_title = row[event_idx].strip()
        clob_tokens = row[clob_idx].strip()
        # Convert escaped quotes
        clob_tokens = clob_tokens.replace('""', '"')
        print(f"   {i+1}. {event_title[:50]}...")
        print(f"      tokens: {clob_tokens[:80]}...")
        csv_tokens.append(clob_tokens)

# Check for any matches
print("\n3. Looking for ANY matches...")
match_count = 0
checked = 0

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, quotechar='"', skipinitialspace=True)
    next(reader)  # skip header
    
    for row in reader:
        checked += 1
        clob_tokens = row[clob_idx].strip().replace('""', '"')
        
        # Check if this exists in database
        result = client.table("markets").select("market_id").eq("clob_token_ids", clob_tokens).limit(1).execute()
        if result.data:
            match_count += 1
            if match_count <= 3:
                print(f"   Match found! Token: {clob_tokens[:60]}...")
        
        if checked >= 100:  # Only check first 100
            break

print(f"\n   Checked {checked} CSV rows, found {match_count} matches")

if match_count == 0:
    print("\n[WARNING] No matches found!")
    print("   This means the CSV data has different clob_token_ids than the database.")
    print("   Possible causes:")
    print("   - Database was imported from a different source")
    print("   - CSV contains different markets than what's in database")
    print("   - The clob_token_ids format differs slightly")
