from database import supabase
from config import settings
from fastapi import HTTPException
from utils.security import generate_session_token, hash_password, verify_password, mask_email, mask_phone
from utils.validators import detect_identifier_type
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def check_device_limit(device_fingerprint: str):
    """Check if device has reached account creation limit"""
    
    # Query users with this device fingerprint
    response = supabase.table("users").select("device_fingerprints").execute()
    
    count = 0
    for user in response.data:
        fingerprints = user.get('device_fingerprints', [])
        if device_fingerprint in fingerprints:
            count += 1
    
    if count >= settings.MAX_ACCOUNTS_PER_DEVICE:
        raise HTTPException(429, "Maximum accounts reached for this device")
    
    return True


async def create_user(email: str, phone: str, full_name: str, city: str, profession: str, device_fingerprint: str):
    """Create new user account"""
    
    # Check device limit
    await check_device_limit(device_fingerprint)
    
    # Check if email or phone already exists
    existing = supabase.table("users").select("*").or_(f"email.eq.{email},phone.eq.{phone}").execute()
    
    if existing.data:
        existing_user = existing.data[0]
        if existing_user['email'] == email:
            raise HTTPException(400, "Email already registered")
        if existing_user['phone'] == phone:
            raise HTTPException(400, "Phone number already registered")
    
    # Create user
    user_data = {
        "email": email,
        "phone": phone,
        "full_name": full_name,
        "city": city,
        "profession": profession,
        "device_fingerprints": [device_fingerprint],
        "email_verified": False,
        "phone_verified": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    response = supabase.table("users").insert(user_data).execute()
    
    if not response.data:
        raise HTTPException(500, "Failed to create user")
    
    user = response.data[0]
    logger.info(f"✅ User created: {user['id']}")
    
    return user


async def create_free_trial_plan(user_id: str):
    """Create free trial plan for new user"""
    
    plan_data = {
        "user_id": user_id,
        "plan_type": "free_trial",
        "status": "active",
        "documents_limit": 1,
        "documents_used": 0,
        "documents_remaining": 1,
        "amount_paid": 0,
        "period_start": datetime.utcnow().date().isoformat(),
        "period_end": (datetime.utcnow().date() + timedelta(days=365*10)).isoformat(),  # 10 years
        "activated_at": datetime.utcnow().isoformat()
    }
    
    response = supabase.table("user_plans").insert(plan_data).execute()
    
    if not response.data:
        raise HTTPException(500, "Failed to create free trial plan")
    
    logger.info(f"✅ Free trial plan created for user {user_id}")
    return response.data[0]


async def mark_user_verified(user_id: str):
    """Mark user as email and phone verified"""
    
    supabase.table("users").update({
        "email_verified": True,
        "phone_verified": True,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", user_id).execute()
    
    logger.info(f"✅ User {user_id} marked as verified")


async def create_session(user_id: str, device_fingerprint: str, remember_me: bool = False):
    """Create user session"""
    
    session_token = generate_session_token()
    expires_days = settings.SESSION_EXPIRE_DAYS if remember_me else 1
    
    session_data = {
        "user_id": user_id,
        "session_token": session_token,
        "device_fingerprint": device_fingerprint,
        "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    response = supabase.table("user_sessions").insert(session_data).execute()
    
    if not response.data:
        raise HTTPException(500, "Failed to create session")
    
    logger.info(f"✅ Session created for user {user_id}")
    return session_token


async def get_user_with_plan(user_id: str):
    """Get user details with active plan"""
    
    # Get user
    user_response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user_response.data:
        raise HTTPException(404, "User not found")
    
    user = user_response.data[0]
    
    # Get active plan
    plan_response = supabase.rpc('get_active_plan', {'p_user_id': user_id}).execute()
    plan = plan_response.data[0] if plan_response.data else None
    
    return {
        "user": {
            "id": user['id'],
            "name": user['full_name'],
            "email": user['email'],
            "phone": user['phone'],
            "city": user.get('city'),
            "profession": user.get('profession')
        },
        "plan": plan
    }


async def verify_session_token(session_token: str):
    """Verify session token and return user"""
    
    # Find session
    response = supabase.table("user_sessions").select("*").eq("session_token", session_token).execute()
    
    if not response.data:
        raise HTTPException(401, "Invalid session")
    
    session = response.data[0]
    
    # Check expiry
    expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00').replace('+00:00', ''))
    if expires_at < datetime.utcnow():
        raise HTTPException(401, "Session expired")
        
    return session
