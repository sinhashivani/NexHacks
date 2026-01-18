"""
Populate Related Trades Table
Batch process to analyze markets and populate the related_trades table
with high-confidence relationships.
"""

import sys
import os
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_connection import SupabaseConnection


def _load_existing_pairs(client, relationship_type: str):
    """Load (market_id, related_market_id) pairs already in DB. Returns set of (min, max) for symmetry."""
    seen = set()
    page_size = 1000
    offset = 0
    while True:
        r = client.table("related_trades").select("market_id, related_market_id").eq(
            "relationship_type", relationship_type
        ).order("id").range(offset, offset + page_size - 1).execute()
        if not r.data:
            break
        for row in r.data:
            a, b = row.get("market_id"), row.get("related_market_id")
            if a and b:
                seen.add((min(a, b), max(a, b)))
        if len(r.data) < page_size:
            break
        offset += page_size
    return seen


def _insert_batch(client, rows: List[Dict], batch: int = 1200):
    """Insert in chunks. On unique violation, skip that chunk and continue. batch 1200 = fewer round-trips."""
    inserted = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i : i + batch]
        try:
            client.table("related_trades").insert(chunk).execute()
            inserted += len(chunk)
        except Exception as e:
            err = str(e)
            if "duplicate" in err.lower() or "unique" in err.lower() or "23505" in err:
                # Try one-by-one to avoid failing whole batch
                for r in chunk:
                    try:
                        client.table("related_trades").insert(r).execute()
                        inserted += 1
                    except Exception:
                        pass
            elif "Could not find the table" in err or "PGRST205" in err:
                raise
            else:
                raise
    return inserted


def populate_event_relationships(client, insert_batch_size: int = 1200):
    """
    Populate related_trades with event relationships (same event_title).
    Uses batched inserts and a one-time load of existing pairs (no per-pair existence check).
    """
    print("=" * 60)
    print("Populating Event Relationships")
    print("=" * 60)
    
    # One-time load of existing pairs (avoids 1 API call per pair)
    print("  Loading existing event relationships...")
    existing = _load_existing_pairs(client, "event")
    print(f"  Found {len(existing)} existing pairs in DB")
    
    # Get all unique event titles
    events_response = client.table("markets").select(
        "event_title"
    ).not_.is_("event_title", "null").execute()
    
    event_titles = [m.get("event_title") for m in events_response.data if m.get("event_title")]
    event_titles = sorted(set(event_titles))
    print(f"  Found {len(event_titles)} unique events")
    
    to_insert = []
    skipped = 0
    total_inserted = 0
    
    for idx, event_title in enumerate(event_titles):
        markets_response = client.table("markets").select("market_id").eq(
            "event_title", event_title
        ).execute()
        
        market_ids = [m.get("market_id") for m in markets_response.data if m.get("market_id")]
        
        for i, a in enumerate(market_ids):
            for b in market_ids[i + 1 :]:
                if not a or not b:
                    continue
                canonical = (min(a, b), max(a, b))
                if canonical in existing:
                    skipped += 1
                    continue
                existing.add(canonical)
                desc = (f"Same event: {event_title}")[:500]
                to_insert.append({
                    "market_id": a, "related_market_id": b,
                    "relationship_type": "event", "relationship_strength": 1.0, "description": desc
                })
                to_insert.append({
                    "market_id": b, "related_market_id": a,
                    "relationship_type": "event", "relationship_strength": 1.0, "description": desc
                })
        
        # Flush when we have enough (larger batch = fewer API round-trips)
        if len(to_insert) >= insert_batch_size:
            added = _insert_batch(client, to_insert, insert_batch_size)
            total_inserted += added
            to_insert = []
            print(f"  Events {idx+1}/{len(event_titles)} | Inserted {total_inserted} rows, skipped {skipped} duplicates")
    
    if to_insert:
        added = _insert_batch(client, to_insert, insert_batch_size)
        total_inserted += added
        print(f"  Final batch: {added} rows")
    
    print(f"\n[OK] Event relationships: {total_inserted} inserted, {skipped} skipped (duplicates)")
    return total_inserted


def populate_sector_relationships(client, insert_batch_size: int = 1200, per_market_cap: int = 200):
    """
    Populate related_trades with sector relationships (same tag_label).
    Uses batched inserts and a one-time load of existing pairs.
    per_market_cap: max sector links per market (avoids millions of rows in big categories).
    """
    print("\n" + "=" * 60)
    print("Populating Sector Relationships")
    print("=" * 60)
    
    print("  Loading existing sector relationships...")
    existing = _load_existing_pairs(client, "sector")
    print(f"  Found {len(existing)} existing pairs in DB")
    
    tags_response = client.table("markets").select("tag_label").not_.is_("tag_label", "null").execute()
    tag_labels = sorted(set(m.get("tag_label") for m in tags_response.data if m.get("tag_label")))
    print(f"  Found {len(tag_labels)} unique categories (max {per_market_cap} sector links per market)")
    
    to_insert = []
    skipped = 0
    capped = 0  # pairs skipped due to per-market cap
    total_inserted = 0
    strength = 0.7
    # per market: how many sector rows with this market_id we've queued this run
    sector_count: Dict[str, int] = {}
    
    for idx, tag_label in enumerate(tag_labels):
        markets_response = client.table("markets").select("market_id, event_title").eq(
            "tag_label", tag_label
        ).execute()
        
        market_data = [(m.get("market_id"), m.get("event_title")) for m in markets_response.data if m.get("market_id")]
        
        for i, (a, event_1) in enumerate(market_data):
            for b, event_2 in market_data[i + 1 :]:
                if not a or not b:
                    continue
                if event_1 == event_2:
                    continue  # same event: already in event relationships
                if sector_count.get(a, 0) >= per_market_cap or sector_count.get(b, 0) >= per_market_cap:
                    capped += 1
                    continue
                canonical = (min(a, b), max(a, b))
                if canonical in existing:
                    skipped += 1
                    continue
                existing.add(canonical)
                sector_count[a] = sector_count.get(a, 0) + 1
                sector_count[b] = sector_count.get(b, 0) + 1
                desc = (f"Same category: {tag_label}")[:500]
                to_insert.append({
                    "market_id": a, "related_market_id": b,
                    "relationship_type": "sector", "relationship_strength": strength, "description": desc
                })
                to_insert.append({
                    "market_id": b, "related_market_id": a,
                    "relationship_type": "sector", "relationship_strength": strength, "description": desc
                })
        
        if len(to_insert) >= insert_batch_size:
            added = _insert_batch(client, to_insert, insert_batch_size)
            total_inserted += added
            to_insert = []
            print(f"  Categories {idx+1}/{len(tag_labels)} | Inserted {total_inserted} rows, skipped {skipped}, capped {capped}")
    
    if to_insert:
        added = _insert_batch(client, to_insert, insert_batch_size)
        total_inserted += added
        print(f"  Final batch: {added} rows")
    
    print(f"\n[OK] Sector relationships: {total_inserted} inserted, {skipped} skipped (duplicates), {capped} skipped (per-market cap)")
    return total_inserted


def check_table_exists(client):
    """Check if related_trades table exists"""
    try:
        # Try a simple query to see if table exists
        client.table("related_trades").select("id").limit(1).execute()
        return True
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            return False
        # Other errors might mean table exists but is empty or has issues
        return True


def main():
    """Main function to populate related_trades table"""
    print("=" * 60)
    print("Populate Related Trades Table")
    print("=" * 60)
    print()
    
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        print("[OK] Connected to Supabase\n")
        
        # Check if table exists
        if not check_table_exists(client):
            print("[ERROR] The 'related_trades' table does not exist!")
            print("\nPlease run the migration first:")
            print("  1. Go to your Supabase dashboard")
            print("  2. Run the SQL from: database/migrations/006_create_related_trades_table.sql")
            print("  OR")
            print("  3. Execute this SQL in Supabase SQL Editor:")
            print()
            print("CREATE TABLE IF NOT EXISTS related_trades (")
            print("    id BIGSERIAL PRIMARY KEY,")
            print("    market_id TEXT NOT NULL REFERENCES markets(market_id),")
            print("    related_market_id TEXT NOT NULL REFERENCES markets(market_id),")
            print("    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('company_pair', 'sector', 'event', 'geographic')),")
            print("    relationship_strength DECIMAL(5, 4) NOT NULL CHECK (relationship_strength >= 0 AND relationship_strength <= 1),")
            print("    description TEXT,")
            print("    examples TEXT[],")
            print("    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),")
            print("    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),")
            print("    UNIQUE(market_id, related_market_id, relationship_type)")
            print(");")
            print()
            print("CREATE INDEX IF NOT EXISTS idx_related_market_id ON related_trades(market_id);")
            print("CREATE INDEX IF NOT EXISTS idx_related_related_market_id ON related_trades(related_market_id);")
            print("CREATE INDEX IF NOT EXISTS idx_related_type ON related_trades(relationship_type);")
            print()
            sys.exit(1)
        
        print("[OK] related_trades table exists\n")
        
        total_inserted = 0
        
        # Populate event relationships
        total_inserted += populate_event_relationships(client)
        
        # Populate sector relationships
        total_inserted += populate_sector_relationships(client)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Population Complete")
        print("=" * 60)
        print(f"Total relationships inserted: {total_inserted}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to populate related_trades: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
