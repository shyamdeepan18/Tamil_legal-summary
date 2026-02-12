from database import supabase
from utils.security import generate_otp
from services.email_service import send_email_otp, send_sms_otp
from datetime import datetime, timedelta
from config import settings
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def create_and_send_otps(user_id: str, email: str, phone: str, name: str, otp_type_prefix: str):
    """
    Create OTP records and send via email & SMS
    otp_type_prefix: 'signup' or 'login'
    """
    
    # Generate OTPs
    email_otp = generate_otp()
    phone_otp = generate_otp()
    
    expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
    
    # Save OTPs to database
    otp_records = [
        {
            "user_id": user_id,
            "otp_type": f"email_{otp_type_prefix}",
            "otp_code": email_otp,
            "destination": email,
            "expires_at": expires_at
        },
        {
            "user_id": user_id,
            "otp_type": f"phone_{otp_type_prefix}",
            "otp_code": phone_otp,
            "destination": phone,
            "expires_at": expires_at
        }
    ]
    
    try:
        supabase.table("otp_verifications").insert(otp_records).execute()
        logger.info(f"✅ OTPs created for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to create OTP records: {e}")
        raise HTTPException(500, "Failed to create OTP records")
    
    # Send OTPs
    try:
        await send_email_otp(email, email_otp, name)
        await send_sms_otp(phone, phone_otp)
        logger.info(f"✅ OTPs sent to {email} and {phone}")
    except Exception as e:
        logger.warning(f"⚠️ OTP send partial failure: {e}")
        # Continue even if sending fails (OTPs are in DB for testing)
    
    return {
        "email_otp": email_otp,  # For testing only! Remove in production
        "phone_otp": phone_otp   # For testing only! Remove in production
    }


async def verify_otp(user_id: str, otp_code: str, otp_type: str) -> bool:
    """Verify OTP code"""
    
    # Find OTP record
    response = supabase.table("otp_verifications").select("*").match({
        "user_id": user_id,
        "otp_type": otp_type,
        "otp_code": otp_code,
        "is_verified": False
    }).execute()
    
    if not response.data:
        raise HTTPException(400, "Invalid or expired OTP")
    
    otp_record = response.data[0]
    
    # Check expiry
    expires_at = datetime.fromisoformat(otp_record['expires_at'].replace('Z', '+00:00').replace('+00:00', ''))
    if expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")
    
    # Check attempts
    if otp_record.get('attempts', 0) >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(429, "Maximum OTP attempts exceeded")
    
    # Mark as verified
    supabase.table("otp_verifications").update({
        "is_verified": True,
        "verified_at": datetime.utcnow().isoformat()
    }).eq("id", otp_record['id']).execute()
    
    logger.info(f"✅ OTP verified for user {user_id}")
    return True


async def resend_otp(user_id: str, otp_type: str):
    """Resend OTP (mark old as expired, create new)"""
    
    # Get user info
    user_response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user_response.data:
        raise HTTPException(404, "User not found")
    
    user = user_response.data[0]
    
    # Invalidate old OTPs
    supabase.table("otp_verifications").update({
        "is_verified": True  # Mark as used
    }).match({
        "user_id": user_id,
        "otp_type": otp_type,
        "is_verified": False
    }).execute()
    
    # Determine type and send new OTP
    if 'email' in otp_type:
        new_otp = generate_otp()
        expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
        
        supabase.table("otp_verifications").insert({
            "user_id": user_id,
            "otp_type": otp_type,
            "otp_code": new_otp,
            "destination": user['email'],
            "expires_at": expires_at
        }).execute()
        
        await send_email_otp(user['email'], new_otp, user['full_name'])
        return {"message": "OTP resent to email"}
    
    elif 'phone' in otp_type:
        new_otp = generate_otp()
        expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
        
        supabase.table("otp_verifications").insert({
            "user_id": user_id,
            "otp_type": otp_type,
            "otp_code": new_otp,
            "destination": user['phone'],
            "expires_at": expires_at
        }).execute()
        
        await send_sms_otp(user['phone'], new_otp)
        return {"message": "OTP resent to phone"}
    
    else:
        raise HTTPException(400, "Invalid OTP type")
