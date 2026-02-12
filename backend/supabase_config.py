from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL:
    print("WARNING: SUPABASE_URL not found")

# Try Service Key first, then Anon Key
key_to_use = SUPABASE_SERVICE_KEY
if not key_to_use or not key_to_use.startswith('eyJ'):
    print("WARNING: Service Key specific format looks invalid (not a JWT). Trying Anon Key.")
    key_to_use = SUPABASE_ANON_KEY

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, key_to_use)
except Exception as e:
    print(f"Initialization Failed: {e}")
    # Fallback to verify if it was just the key format
    if key_to_use != SUPABASE_ANON_KEY:
         print("Retrying with Anon Key...")
         supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Helper functions for the application
async def get_user_by_email(email: str):
    """Get user by email"""
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

async def get_user_by_phone(phone: str):
    """Get user by phone"""
    response = supabase.table("users").select("*").eq("phone", phone).execute()
    return response.data[0] if response.data else None

async def get_active_plan(user_id: str):
    """Get user's active plan"""
    response = supabase.rpc('get_active_plan', {'p_user_id': user_id}).execute()
    return response.data[0] if response.data else None

async def use_document(user_id: str):
    """Decrement document count"""
    try:
        response = supabase.rpc('use_document', {'p_user_id': user_id}).execute()
        return True
    except Exception as e:
        raise Exception(f"Document limit reached: {str(e)}")

# Test connection
def test_connection():
    """Test database connection"""
    print(f"Connecting to Supabase at: {SUPABASE_URL}")
    try:
        # Check connection by querying a public table or just checking health
        # Trying 'users' table as per prompt, handling case where it might be empty
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Database connected! Users count: {result.count}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Run test if executed directly
if __name__ == "__main__":
    test_connection()
