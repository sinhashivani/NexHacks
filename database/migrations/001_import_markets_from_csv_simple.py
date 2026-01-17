"""
Migration: Import Markets from CSV (Simple Version)
Imports polymarket_events_by_tags.csv into the markets table
Uses built-in csv module instead of pandas to avoid numpy issues
"""

import sys
import os
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.supabase_connection import SupabaseConnection


def import_markets_from_csv(csv_path: str = "polymarket_events_by_tags.csv"):
    """
    Import markets from CSV file into Supabase markets table
    
    Args:
        csv_path: Path to the CSV file
    """
    print("=" * 60)
    print("CSV Import Migration - Simple Version")
    print("=" * 60)
    print()
    
    print(f"Reading CSV file: {csv_path}")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        print(f"   Make sure the file is in the project root directory")
        return False
    
    # Connect to Supabase first
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        print("[OK] Connected to Supabase")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {e}")
        print("   Make sure SUPABASE_URL and SUPABASE_ANON_KEY are in .env file")
        return False
    
    # Read and process CSV
    records = []
    skipped = 0
    total_rows = 0
    
    print("\nReading CSV file...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                total_rows += 1
                
                # Skip rows with missing market_id (required)
                market_id = row.get('market_id', '').strip()
                if not market_id:
                    skipped += 1
                    continue
                
                # Prepare record
                record = {
                    "market_id": market_id,
                    "market_slug": row.get('market_slug', '').strip() or None,
                    "question": row.get('question', '').strip() or "",
                    "tag_label": row.get('tag_label', '').strip() or None,
                    "tag_id": int(row['tag_id']) if row.get('tag_id') and row['tag_id'].strip() else None,
                    "clob_token_ids": row.get('clob_token_ids', '').strip() or None,
                    "active": True,
                    "closed": False
                }
                records.append(record)
                
                # Show progress every 1000 rows
                if total_rows % 1000 == 0:
                    print(f"  Processed {total_rows} rows...")
    
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"[OK] Read {total_rows} rows from CSV")
    if skipped > 0:
        print(f"[WARNING] Skipped {skipped} rows with missing market_id")
    print(f"[OK] Prepared {len(records)} records for insertion")
    
    # Insert data in batches
    batch_size = 100
    total_inserted = 0
    errors = 0
    
    print(f"\nInserting data in batches of {batch_size}...")
    print()
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        try:
            # Use upsert to handle duplicates (update if exists, insert if not)
            response = client.table("markets").upsert(
                batch,
                on_conflict="market_id"
            ).execute()
            
            total_inserted += len(batch)
            
            # Show progress
            if batch_num % 10 == 0 or batch_num == total_batches:
                progress = min(i + batch_size, len(records))
                print(f"  Progress: {batch_num}/{total_batches} batches ({progress}/{len(records)} records)")
        
        except Exception as e:
            errors += 1
            print(f"[ERROR] Batch {batch_num} failed: {e}")
            # Continue with next batch
            continue
    
    print()
    print("=" * 60)
    print("[SUCCESS] Migration complete!")
    print("=" * 60)
    print(f"  Total records processed: {total_inserted}")
    print(f"  Errors: {errors}")
    
    # Verify import
    try:
        result = client.table("markets").select("count", count="exact").execute()
        total_count = result.count if hasattr(result, 'count') else 0
        print(f"  Total markets in database: {total_count}")
    except Exception as e:
        print(f"  [WARNING] Could not verify total count: {e}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import markets from CSV to Supabase")
    parser.add_argument(
        "--csv",
        type=str,
        default="polymarket_events_by_tags.csv",
        help="Path to CSV file (default: polymarket_events_by_tags.csv)"
    )
    
    args = parser.parse_args()
    
    try:
        success = import_markets_from_csv(args.csv)
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
