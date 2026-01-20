import os
import logging
from datetime import datetime
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.client: Client = None

        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("✅ Connected to Supabase via API.")
            except Exception as e:
                logger.error(f"❌ Failed to init Supabase client: {e}")
        else:
            logger.warning("⚠️ SUPABASE_URL or SUPABASE_KEY missing. History will not be saved.")

    def add_message(self, session_id, role, content):
        """
        Saves a message to the 'conversations' table.
        """
        if not self.client:
            return

        try:
            data = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
            self.client.table("conversations").insert(data).execute()
            
        except Exception as e:
            logger.error(f"Supabase Insert Error: {e}")

    def get_history(self, session_id, limit=10):
        """
        Retrieves the last N messages for a specific session.
        """
        if not self.client:
            return []

        try:
            response = self.client.table("conversations")\
                .select("role, content")\
                .eq("session_id", session_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data[::-1]
            
        except Exception as e:
            logger.error(f"Supabase Fetch Error: {e}")
            return []