"""
Migration: Import Similarity Scores from CSV
Imports similarity_scores.csv into the similarity_scores table
"""

import sys
import os
import csv
import json
import re

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
        # Parse JSON array and re-serialize with consistent formatting
        token_ids = json.loads(token_ids_str)
        if isinstance(token_ids, list):
            # Sort and normalize
            normalized = sorted([str(tid).strip() for tid in token_ids if str(tid).strip()])
            return json.dumps(normalized, separators=(',', ':'))
        return token_ids_str.strip()
    except (json.JSONDecodeError, TypeError):
        return token_ids_str.strip()


def _parse_row(cols):
    """
    Parse a CSV row into (source_ids, neighbor_ids, similarity_float) or (None,None,None).
    Handles 3-column rows and 4-column rows (neighbor JSON is split at its internal comma).
    """
    if len(cols) == 3:
        source_raw, neighbor_raw, sim_raw = cols[0].strip(), cols[1].strip(), cols[2].strip()
    elif len(cols) >= 4:
        # Neighbor was split: col1 = start of neighbor, col2 = end of neighbor, col3 = cosine
        source_raw = cols[0].strip()
        neighbor_raw = (cols[1] + ',' + cols[2]).strip()
        sim_raw = cols[3].strip()
    else:
        return None, None, None

    source_ids = normalize_token_ids(source_raw)
    neighbor_ids = normalize_token_ids(neighbor_raw)

    # Ensure neighbor is valid JSON (joined col1+col2 can be malformed); salvage by extracting two token IDs
    try:
        json.loads(neighbor_ids)
    except (json.JSONDecodeError, TypeError):
        neighbor_ids = ""
    if not neighbor_ids and len(cols) >= 4:
        combined = (cols[1] + " " + cols[2])
        tokens = re.findall(r"\d{50,}", combined)
        if len(tokens) >= 2:
            neighbor_ids = json.dumps(sorted(tokens), separators=(",", ":"))

    if not source_ids or not neighbor_ids:
        return None, None, None

    try:
        sim = float(sim_raw)
        if sim < 0 or sim > 1:
            return None, None, None
        return source_ids, neighbor_ids, sim
    except (ValueError, TypeError):
        return None, None, None


def import_similarity_scores(csv_path: str = "similarity_scores.csv"):
    """
    Import similarity scores from CSV file into Supabase similarity_scores table
    
    Args:
        csv_path: Path to the similarity_scores.csv file
    """
    print("=" * 60)
    print("Similarity Scores Import Migration")
    print("=" * 60)
    print()
    
    print(f"Reading CSV file: {csv_path}")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        print(f"   Make sure the file is in the project root directory")
        return False
    
    # Connect to Supabase
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        print("[OK] Connected to Supabase")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {e}")
        print("   Make sure SUPABASE_URL and SUPABASE_ANON_KEY are in .env file")
        return False
    
    # Read and process CSV (use csv.reader: DictReader breaks on header/column spacing and neighbor split)
    records = []
    skipped = 0
    total_rows = 0
    
    print("\nReading CSV file...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, quotechar='"', doublequote=True)
            next(reader)  # skip header
            
            for row in reader:
                total_rows += 1
                source_ids, neighbor_ids, sim = _parse_row(row)
                if source_ids is None:
                    skipped += 1
                    continue
                records.append({
                    "source_clob_token_ids": source_ids,
                    "neighbor_clob_token_ids": neighbor_ids,
                    "cosine_similarity": sim
                })
                if total_rows % 10000 == 0:
                    print(f"  Processed {total_rows} rows...")
    
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"[OK] Read {total_rows} rows from CSV")
    if skipped > 0:
        print(f"[WARNING] Skipped {skipped} rows with missing/invalid data")
    print(f"[OK] Prepared {len(records)} records for insertion")
    
    # Insert data in batches
    batch_size = 1000
    total_inserted = 0
    errors = 0
    
    print(f"\nInserting data in batches of {batch_size}...")
    print()
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        try:
            # Insert batch
            response = client.table("similarity_scores").insert(batch).execute()
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
        result = client.table("similarity_scores").select("count", count="exact").execute()
        total_count = result.count if hasattr(result, 'count') else 0
        print(f"  Total similarity scores in database: {total_count}")
    except Exception as e:
        print(f"  [WARNING] Could not verify total count: {e}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import similarity scores from CSV to Supabase")
    parser.add_argument(
        "--csv",
        type=str,
        default="similarity_scores.csv",
        help="Path to similarity_scores.csv file (default: similarity_scores.csv)"
    )
    
    args = parser.parse_args()
    
    try:
        success = import_similarity_scores(args.csv)
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
