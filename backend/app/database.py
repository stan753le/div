import os
from app.config import settings

# If `USE_SQLITE` is set to a truthy value in the environment, use the local
# SQLite adapter which mimics the minimal supabase.table(...).select(...).execute()
# API used across the backend. Otherwise, use the real Supabase client.
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() in ("1", "true", "yes")

if USE_SQLITE:
	from app.sqlite_adapter import create_client
	supabase = create_client(settings.sqlite_db_path)
else:
	from supabase import create_client, Client
	supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)
