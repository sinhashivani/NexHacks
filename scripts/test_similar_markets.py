"""
Test Script for Similar Markets Functionality
Tests the get_similar_by_event_title function and similarity system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polymarket.get_similar_markets import get_similar_by_event_title
from database.supabase_connection import SupabaseConnection


def test_database_connection():
    """Test if database connection works"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        
        # Test markets table
        result = client.table("markets").select("count", count="exact").limit(1).execute()
        market_count = result.count if hasattr(result, 'count') else 0
        print(f"✓ Markets table accessible: {market_count} markets found")
        
        # Test similarity_scores table
        result = client.table("similarity_scores").select("count", count="exact").limit(1).execute()
        similarity_count = result.count if hasattr(result, 'count') else 0
        print(f"✓ Similarity scores table accessible: {similarity_count} similarity scores found")
        
        # Check if event_title column exists
        sample = client.table("markets").select("event_title").limit(1).execute()
        if sample.data:
            print(f"✓ event_title column exists in markets table")
        else:
            print(f"⚠ No markets found to verify event_title column")
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_find_event_titles():
    """Find available event titles in the database"""
    print("\n" + "=" * 60)
    print("Finding Available Event Titles")
    print("=" * 60)
    try:
        conn = SupabaseConnection()
        client = conn.get_client()
        
        # Get distinct event titles
        result = client.table("markets").select("event_title").limit(100).execute()
        
        event_titles = set()
        for market in result.data:
            event_title = market.get("event_title")
            if event_title:
                event_titles.add(event_title)
        
        print(f"Found {len(event_titles)} unique event titles (showing first 10):")
        for i, title in enumerate(sorted(event_titles)[:10], 1):
            print(f"  {i}. {title}")
        
        if len(event_titles) > 10:
            print(f"  ... and {len(event_titles) - 10} more")
        
        return list(event_titles)
    except Exception as e:
        print(f"✗ Failed to find event titles: {e}")
        return []


def test_similar_markets(event_title: str):
    """Test getting similar markets for a given event title"""
    print("\n" + "=" * 60)
    print(f"Testing Similar Markets for: {event_title}")
    print("=" * 60)
    
    try:
        result = get_similar_by_event_title(event_title, limit=5)
        
        print(f"\nEvent Title: {result.get('event_title')}")
        print(f"Number of clob_token_ids: {len(result.get('clob_token_ids', []))}")
        print(f"Number of event markets: {len(result.get('event_markets', []))}")
        print(f"Number of similar markets found: {result.get('count', 0)}")
        
        if result.get('error'):
            print(f"\n✗ Error: {result.get('error')}")
            return False
        
        if result.get('message'):
            print(f"\n⚠ {result.get('message')}")
            return False
        
        # Show event markets
        event_markets = result.get('event_markets', [])
        if event_markets:
            print(f"\nEvent Markets ({len(event_markets)}):")
            for i, market in enumerate(event_markets[:3], 1):
                print(f"  {i}. {market.get('question', 'N/A')[:80]}")
                print(f"     Market ID: {market.get('market_id', 'N/A')}")
                print(f"     Token IDs: {market.get('clob_token_ids', 'N/A')[:60]}...")
            if len(event_markets) > 3:
                print(f"  ... and {len(event_markets) - 3} more")
        
        # Show similar markets
        similar_markets = result.get('similar_markets', [])
        if similar_markets:
            print(f"\nSimilar Markets (Top {len(similar_markets)}):")
            for i, market in enumerate(similar_markets, 1):
                similarity = market.get('cosine_similarity', 0)
                question = market.get('question', 'N/A')
                market_id = market.get('market_id', 'N/A')
                
                print(f"\n  {i}. Similarity: {similarity:.4f}")
                print(f"     Question: {question[:80]}")
                print(f"     Market ID: {market_id}")
                print(f"     Event Title: {market.get('event_title', 'N/A')[:60]}")
                print(f"     Tag: {market.get('tag_label', 'N/A')}")
        else:
            print("\n⚠ No similar markets found")
            print("   This could mean:")
            print("   - No similarity scores exist for this event")
            print("   - Similarity scores haven't been imported yet")
            print("   - Markets with matching token IDs don't exist in database")
        
        return True
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_event_titles(event_titles: list):
    """Test similar markets for multiple event titles"""
    print("\n" + "=" * 60)
    print("Testing Multiple Event Titles")
    print("=" * 60)
    
    results = []
    for event_title in event_titles[:5]:  # Test first 5
        print(f"\n--- Testing: {event_title[:60]} ---")
        result = get_similar_by_event_title(event_title, limit=3)
        
        results.append({
            "event_title": event_title,
            "found": result.get('count', 0) > 0,
            "similar_count": result.get('count', 0),
            "has_error": 'error' in result
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    successful = sum(1 for r in results if r['found'] and not r['has_error'])
    print(f"Successfully found similar markets: {successful}/{len(results)}")
    print(f"Total similar markets found: {sum(r['similar_count'] for r in results)}")
    
    for r in results:
        status = "✓" if r['found'] and not r['has_error'] else "✗"
        print(f"  {status} {r['event_title'][:50]}: {r['similar_count']} similar markets")


def main():
    """Main test function"""
    print("=" * 60)
    print("Similar Markets Functionality Test")
    print("=" * 60)
    print()
    
    # Test 1: Database connection
    if not test_database_connection():
        print("\n✗ Cannot proceed without database connection")
        return
    
    # Test 2: Find event titles
    event_titles = test_find_event_titles()
    
    if not event_titles:
        print("\n⚠ No event titles found in database.")
        print("   You may need to run migration 005_update_markets_with_event_title.py")
        return
    
    # Test 3: Test with a specific event title
    test_event_title = event_titles[0] if event_titles else None
    
    if test_event_title:
        print(f"\n{'=' * 60}")
        print("Single Event Title Test")
        print("=" * 60)
        test_similar_markets(test_event_title)
    
    # Test 4: Test multiple event titles
    if len(event_titles) > 1:
        test_multiple_event_titles(event_titles)
    
    # Test 5: Test with non-existent event title
    print("\n" + "=" * 60)
    print("Testing Non-Existent Event Title")
    print("=" * 60)
    test_similar_markets("This Event Title Does Not Exist 12345")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] Test failed with exception:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
