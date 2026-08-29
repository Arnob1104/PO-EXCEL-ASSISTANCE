from supabase import create_client, Client
from app.config import settings

# NOTE: this client uses the SECRET (service-role) key, which bypasses RLS.
# That's intentional for backend-side operations, but it means every query
# in this codebase MUST manually filter by org_id. Never expose this client
# or key to the frontend.
supabase: Client = create_client(settings.supabase_url, settings.supabase_secret_key)
