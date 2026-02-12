from fastapi import APIRouter, Request, HTTPException, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from config import settings
from database import supabase
from services.auth_service import create_session, create_free_trial_plan
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

# Initialize Authlib
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/login")
async def google_login(request: Request):
    """Redirect user to Google for authentication"""
    redirect_uri = request.url_for('google_auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback", name="google_auth_callback")
async def google_auth_callback(request: Request):
    """Handle callback from Google"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            # Fallback if userinfo not in token (depends on scope/provider)
            user_info = await oauth.google.userinfo(token=token)
            
        email = user_info.get('email')
        name = user_info.get('name')
        
        logger.info(f"Google Auth Success: {email}")
        
        # Check if user exists
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        user_id = None
        
        if response.data:
            # User exists
            user_id = response.data[0]['id']
            logger.info(f"Existing user: {user_id}")
        else:
            # Create new user
            logger.info(f"Creating new user from Google: {email}")
            
            # Use dummy phone for Google users initially (or make nullable in DB)
            # For now, we'll try to insert. If phone is required, this might fail 
            # unless we put a placeholder.
            # Assuming phone is required based on User model.
            
            # Using a placeholder phone that validates but clearly isn't real/verified
            # This is a temporary measure. Ideally make phone optional for OAuth users.
            placeholder_phone = "+910000000000" 
            
            user_data = {
                "email": email,
                "phone": placeholder_phone, 
                "full_name": name,
                "city": "Unknown",
                "profession": "other",
                "device_fingerprints": ["google_oauth"],
                "email_verified": True, # Verified by Google
                "phone_verified": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            new_user_res = supabase.table("users").insert(user_data).execute()
            if not new_user_res.data:
                raise HTTPException(500, "Failed to create user from Google profile")
            
            user_id = new_user_res.data[0]['id']
            await create_free_trial_plan(user_id)
            
        # Create Session
        session_token = await create_session(
            user_id, 
            "google_oauth", 
            remember_me=True
        )
        
        # Redirect to frontend with token
        frontend_url = settings.FRONTEND_URL
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={session_token}")
        
    except Exception as e:
        logger.error(f"Google Auth Error: {str(e)}")
        # Redirect to login with error
        frontend_url = settings.FRONTEND_URL
        return RedirectResponse(url=f"{frontend_url}/login?error=Google_Auth_Failed")
