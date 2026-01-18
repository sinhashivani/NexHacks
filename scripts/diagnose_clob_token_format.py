"""
Diagnostic script to compare clob_token_ids format between CSV and database
"""

import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_connection import SupabaseConnection

def normalize_token_ids(token_ids_str: str) -> str:
    """Normalize clob_token_ids to consistent format"""
    if not token_ids_str or token_ids_str.strip().lower() == 'none':
        return ""
    
    try:
        token_ids = json.loads(token_ids_str)
        if isinstance(token_ids, list):
            normalized = sorted([str(tid).strip() for tid in token_ids if str(tid).strip()])
            return json.dumps(normalized, separators=(',', ':'))
        return token_ids_str.strip()
    except (json.JSONDecodeError, TypeError):
        return token_ids_str.strip()

def main():
    print("=" * 60)
    print("Clob Token IDs Format Diagnostic")
    print("=" * 60)
    
    # Check CSV format
    print("\n1. Checking CSV format...")
    try:
        csv_path = 'data/polymarket_events_by_tags.csv'
        if not os.path.exists(csv_path):
            print(f"  ERROR: CSV file not found at {csv_path}")
            return
        
        # Try different pandas parsing options
        print("  Trying standard pandas read_csv...")
        try:
            df1 = pd.read_csv(csv_path, encoding='utf-8')
            print(f"    Columns: {list(df1.columns)}")
            if len(df1) > 0:
                if 'clob_token_ids' in df1.columns:
                    sample = str(df1.iloc[0]['clob_token_ids'])
                    print(f"    Sample (first 100 chars): {repr(sample[:100])}")
                else:
                    print(f"    WARNING: 'clob_token_ids' column not found!")
                    print(f"    Available columns: {list(df1.columns)}")
        except Exception as e:
            print(f"    Error with standard read: {e}")
        
        print("\n  Trying with quotechar and escapechar...")
        try:
            df2 = pd.read_csv(csv_path, encoding='utf-8', 
                             quotechar='"', escapechar='\\', skipinitialspace=True)
            df2.columns = df2.columns.str.strip()
            print(f"    Columns: {list(df2.columns)}")
            if len(df2) > 0:
                if 'clob_token_ids' in df2.columns:
                    sample = str(df2.iloc[0]['clob_token_ids'])
                    print(f"    Sample (first 100 chars): {repr(sample[:100])}")
                    normalized = normalize_token_ids(sample)
                    print(f"    Normalized (first 100 chars): {repr(normalized[:100])}")
                else:
                    print(f"    WARNING: 'clob_token_ids' column not found!")
        except Exception as e:
            print(f"    Error with quotechar read: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"    Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check database format
    print("\n2. Checking database format...")
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        print("  ✓ Connected to database")
        
        # Get sample markets
        markets = client.table("markets").select("market_id, question, clob_token_ids").limit(5).execute()
        
        print(f"  Found {len(markets.data)} sample markets")
        for i, market in enumerate(markets.data[:3], 1):
            token_ids = market.get("clob_token_ids", "")
            question = market.get("question", "")[:50]
            print(f"\n  Market {i}:")
            print(f"    Question: {question}...")
            if token_ids:
                print(f"    clob_token_ids (first 100 chars): {repr(token_ids[:100])}")
                normalized = normalize_token_ids(token_ids)
                print(f"    Normalized (first 100 chars): {repr(normalized[:100])}")
            else:
                print(f"    clob_token_ids: (empty)")
    except Exception as e:
        print(f"    Error connecting to database: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Try to find a match
    print("\n3. Attempting to find a match...")
    try:
        # Get one from CSV
        csv_path = 'data/polymarket_events_by_tags.csv'
        df = pd.read_csv(csv_path, encoding='utf-8', 
                        quotechar='"', escapechar='\\', skipinitialspace=True)
        df.columns = df.columns.str.strip()
        
        if 'clob_token_ids' not in df.columns:
            print("  ERROR: 'clob_token_ids' column not found in CSV")
            return
        
        if len(df) == 0:
            print("  ERROR: CSV is empty")
            return
        
        csv_token_ids = str(df.iloc[0]['clob_token_ids']).strip()
        print(f"  CSV raw (first 100 chars): {repr(csv_token_ids[:100])}")
        
        # Clean up quotes
        if csv_token_ids.startswith('"') and csv_token_ids.endswith('"'):
            csv_token_ids = csv_token_ids[1:-1]
        
        csv_normalized = normalize_token_ids(csv_token_ids)
        print(f"  CSV normalized (first 100 chars): {repr(csv_normalized[:100])}")
        
        # Try to find in database
        conn = SupabaseConnection()
        client = conn.get_client()
        
        # Try exact match with normalized
        print("\n  Trying to match normalized format...")
        result = client.table("markets").select("market_id, question").eq("clob_token_ids", csv_normalized).limit(1).execute()
        if result.data:
            print(f"  ✓ Found exact match with normalized format!")
            print(f"    Matched market: {result.data[0].get('question', '')[:60]}")
        else:
            print(f"  ✗ No exact match with normalized format")
            
            # Try with original format
            print("\n  Trying to match original format...")
            result2 = client.table("markets").select("market_id, question").eq("clob_token_ids", csv_token_ids).limit(1).execute()
            if result2.data:
                print(f"  ✓ Found match with original format!")
                print(f"    Matched market: {result2.data[0].get('question', '')[:60]}")
            else:
                print(f"  ✗ No match with original format either")
                
                # Try partial match - get a sample from database and compare
                print("\n  Comparing formats...")
                db_sample = client.table("markets").select("clob_token_ids").limit(1).execute()
                if db_sample.data:
                    db_token_ids = db_sample.data[0].get("clob_token_ids", "")
                    print(f"  Database sample (first 100 chars): {repr(db_token_ids[:100])}")
                    db_normalized = normalize_token_ids(db_token_ids)
                    print(f"  Database normalized (first 100 chars): {repr(db_normalized[:100])}")
                    
                    if csv_normalized == db_normalized:
                        print("  ✓ Formats match after normalization!")
                    else:
                        print("  ✗ Formats don't match even after normalization")
                        print("  This suggests the markets were imported from a different source")
    except Exception as e:
        print(f"    Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
