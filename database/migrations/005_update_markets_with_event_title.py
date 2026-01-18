"""
Migration: Update Markets with Event Title
Updates existing markets table with event_title from CSV file
Matches markets by clob_token_ids
"""

import sys
import os
import csv
import json

# Force unbuffered output on Windows
sys.stdout.reconfigure(line_buffering=True)

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("[WARNING] pandas not available, will use csv module (may have issues with quoted fields)")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.supabase_connection import SupabaseConnection


def normalize_token_ids(token_ids_str: str) -> str:
    """
    Normalize clob_token_ids to consistent format for matching
    """
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


def update_markets_with_event_title(csv_path: str = "data/polymarket_events_by_tags.csv"):
    """
    Update markets table with event_title from CSV file
    
    Args:
        csv_path: Path to the CSV file
    """
    print("=" * 60)
    print("Update Markets with Event Title Migration")
    print("=" * 60)
    print()
    
    print(f"Reading CSV file: {csv_path}")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        return False
    
    # Connect to Supabase
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        print("[OK] Connected to Supabase")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {e}")
        return False
    
    # Build mapping of clob_token_ids -> event_title from CSV
    csv_mapping = {}
    total_rows = 0
    
    print("\nReading CSV file...")
    try:
        # Use Python's csv module which handles quoted fields correctly
        # Test showed csv.reader works perfectly for this CSV format
        import csv as csv_module
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv_module.reader(f, quotechar='"', skipinitialspace=True)
            
            # Read header
            header = next(reader)
            header = [col.strip() for col in header]
            print(f"  CSV columns found: {header}")
            
            # Find column indices
            event_title_idx = None
            clob_token_ids_idx = None
            for i, col in enumerate(header):
                col_lower = col.strip().lower()
                if 'event_title' in col_lower:
                    event_title_idx = i
                if 'clob_token_ids' in col_lower:
                    clob_token_ids_idx = i
            
            if event_title_idx is None or clob_token_ids_idx is None:
                print(f"[ERROR] Could not find required columns")
                print(f"  event_title_idx: {event_title_idx}, clob_token_ids_idx: {clob_token_ids_idx}")
                return False
            
            print(f"  Using columns: event_title (idx {event_title_idx}), clob_token_ids (idx {clob_token_ids_idx})")
            
            total_rows = 0
            sample_count = 0
            
            # Read data rows
            for row in reader:
                total_rows += 1
                
                if len(row) < max(event_title_idx, clob_token_ids_idx) + 1:
                    continue
                
                event_title = row[event_title_idx].strip() if len(row) > event_title_idx else ''
                clob_token_ids_str = row[clob_token_ids_idx].strip() if len(row) > clob_token_ids_idx else ''
                
                # Clean up clob_token_ids - remove outer quotes if present
                if clob_token_ids_str.startswith('"') and clob_token_ids_str.endswith('"'):
                    clob_token_ids_str = clob_token_ids_str[1:-1]
                
                # Convert escaped quotes ("") to regular quotes (")
                # CSV uses "" to escape quotes, database uses "
                # This is RFC 4180 standard CSV escaping
                if '""' in clob_token_ids_str:
                    clob_token_ids_str = clob_token_ids_str.replace('""', '"')
                
                # Debug: Show first few samples
                if sample_count < 3 and event_title and clob_token_ids_str:
                    print(f"  Sample row {sample_count + 1}:")
                    print(f"    event_title: {event_title[:60]}")
                    print(f"    clob_token_ids (raw): {clob_token_ids_str[:80]}")
                    normalized = normalize_token_ids(clob_token_ids_str)
                    print(f"    clob_token_ids (normalized): {normalized[:80]}")
                    sample_count += 1
                
                if event_title and clob_token_ids_str:
                    # Store ORIGINAL format (not normalized) since database stores original format
                    # Use original as key to match database format
                    if clob_token_ids_str not in csv_mapping:
                        csv_mapping[clob_token_ids_str] = event_title
                
                if total_rows % 1000 == 0:
                    print(f"  Processed {total_rows} rows...")
    
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"[OK] Read {total_rows} rows from CSV")
    print(f"[OK] Found {len(csv_mapping)} unique clob_token_ids with event_title")
    
    if len(csv_mapping) == 0:
        print("\n[WARNING] No clob_token_ids found in CSV!")
        print("  This could mean:")
        print("  - CSV column names don't match expected format")
        print("  - clob_token_ids column is empty or malformed")
        print("  - CSV format is different than expected")
        print("\n  Checking sample of markets in database...")
        
        # Check what clob_token_ids look like in database
        try:
            sample_markets = client.table("markets").select("clob_token_ids").limit(5).execute()
            print("  Sample clob_token_ids from database:")
            for i, market in enumerate(sample_markets.data[:3], 1):
                token_ids = market.get("clob_token_ids", "")
                print(f"    {i}. {token_ids[:80] if token_ids else '(empty)'}")
        except Exception as e:
            print(f"  Could not check database: {e}")
        
        return False
    
    # Update markets in batches
    batch_size = 100
    updated = 0
    not_found = 0
    errors = 0
    
    print(f"\nUpdating markets in batches of {batch_size}...")
    print()
    
    # Process in batches
    csv_items = list(csv_mapping.items())
    
    # Debug: Check first few matches and compare formats
    print("Checking first few matches...")
    print("\nComparing CSV format with database format:")
    
    # Get a sample from database
    db_sample = client.table("markets").select("clob_token_ids").limit(1).execute()
    if db_sample.data:
        db_token_ids = db_sample.data[0].get("clob_token_ids", "")
        db_normalized = normalize_token_ids(db_token_ids)
        print(f"  Database sample (first 100): {repr(db_token_ids[:100])}")
        print(f"  Database normalized (first 100): {repr(db_normalized[:100])}")
    
    for i, (clob_token_ids, event_title) in enumerate(csv_items[:3], 1):
        try:
            print(f"\n  CSV item {i}:")
            print(f"    Format (first 100): {repr(clob_token_ids[:100])}")
            
            # Try match with original format (what database has)
            check = client.table("markets").select("market_id, question").eq("clob_token_ids", clob_token_ids).limit(1).execute()
            if check.data:
                print(f"    [OK] Found match: {check.data[0].get('question', '')[:60]}")
            else:
                print(f"    [X] No match found")
                # Try normalized version as fallback
                csv_normalized = normalize_token_ids(clob_token_ids)
                check2 = client.table("markets").select("market_id, question").eq("clob_token_ids", csv_normalized).limit(1).execute()
                if check2.data:
                    print(f"    [OK] Found match with normalized format!")
                else:
                    print(f"    [X] No match with either format")
                    if db_sample.data:
                        print(f"    Note: CSV format differs from DB sample")
        except Exception as e:
            print(f"    [X] Error checking: {e}")
    
    print()
    
    total_items = len(csv_items)
    total_batches = (total_items + batch_size - 1) // batch_size
    print(f"Processing {total_items} items in {total_batches} batches...")
    sys.stdout.flush()
    
    for i in range(0, total_items, batch_size):
        batch = csv_items[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        for clob_token_ids, event_title in batch:
            try:
                # Update markets with matching clob_token_ids
                response = client.table("markets").update({
                    "event_title": event_title
                }).eq("clob_token_ids", clob_token_ids).execute()
                
                if response.data:
                    updated += len(response.data)
                else:
                    not_found += 1
            
            except Exception as e:
                errors += 1
                if errors <= 5:  # Only print first 5 errors
                    print(f"[ERROR] Failed to update clob_token_ids {clob_token_ids[:50]}...: {e}")
                    sys.stdout.flush()
        
        # Show progress every batch
        progress = min(i + batch_size, total_items)
        print(f"  Batch {batch_num}/{total_batches}: {progress}/{total_items} items | Updated: {updated}, Not found: {not_found}")
        sys.stdout.flush()
    
    print()
    print("=" * 60)
    print("[SUCCESS] Migration complete!")
    print("=" * 60)
    print(f"  Markets updated: {updated}")
    print(f"  Markets not found: {not_found}")
    print(f"  Errors: {errors}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    # Suppress numpy warnings (they're just warnings, not errors)
    import warnings
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    
    print("Script starting...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    parser = argparse.ArgumentParser(description="Update markets with event_title from CSV")
    parser.add_argument(
        "--csv",
        type=str,
        default="data/polymarket_events_by_tags.csv",
        help="Path to CSV file (default: data/polymarket_events_by_tags.csv)"
    )
    
    args = parser.parse_args()
    
    try:
        success = update_markets_with_event_title(args.csv)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] Migration failed with exception:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
