"""
Supabase Connection Handler
Handles connection to Supabase PostgreSQL database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseConnection:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file"
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
    def get_client(self) -> Client:
        """Get Supabase client instance"""
        return self.client
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Simple query to test connection
            response = self.client.table("markets").select("count", count="exact").limit(0).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Connection test failed: {e}")
            return False
