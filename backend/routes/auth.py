from fastapi import APIRouter, HTTPException, Depends, Request
from models.auth import (
    SignupRequest, VerifyOTPRequest, LoginRequest, 
    VerifyLoginOTPRequest, AuthResponse, ForgotPasswordRequest, 
    ResetPasswordRequest
)
from models.user import UserResponse
from services.auth_service import (
    create_user, create_free_trial_plan, mark_user_verified, 
    create_session, get_user_with_plan, verify_session_token
)
from services.otp_service import create_and_send_otps, verify_otp, resend_otp
from services.email_service import send_email_otp, send_sms_otp
from utils.validators import detect_identifier_type
from utils.security import generate_reset_token, hash_password
from database import supabase
from config import settings
import logging
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    # Create user (this checks for duplicates)
    user = await create_user(
        email=request.email,
        phone=request.phone,
        full_name=request.full_name,
        city=request.city,
        profession=request.profession,
        device_fingerprint=request.device_fingerprint
    )
    
    # Create free trial plan
    await create_free_trial_plan(user['id'])
    
    # Send OTPs
    await create_and_send_otps(
        user_id=user['id'], 
        email=user['email'], 
        phone=user['phone'], 
        name=user['full_name'], 
        otp_type_prefix="signup"
    )
    
    return AuthResponse(
        success=True,
        message="Account created. OTPs sent to email and phone.",
        user={"id": user['id']}
    )

@router.post("/verify-signup", response_model=AuthResponse)
async def verify_signup(request: VerifyOTPRequest):
    # Verify Email OTP
    await verify_otp(request.user_id, request.email_otp, "email_signup")
    
    # Verify Phone OTP
    await verify_otp(request.user_id, request.phone_otp, "phone_signup")
    
    # Mark user verified
    await mark_user_verified(request.user_id)
    
    # Get user details
    user_data = await get_user_with_plan(request.user_id)
    
    return AuthResponse(
        success=True,
        message="Account verified successfully. Please login.",
        user=user_data['user']
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    id_type, identifier = detect_identifier_type(request.identifier)
    
    # Find user
    column = "email" if id_type == "email" else "phone"
    response = supabase.table("users").select("*").eq(column, identifier).execute()
    
    if not response.data:
        raise HTTPException(404, "User not found")
        
    user = response.data[0]
    
    otp_type = f"{id_type}_login"
    
    # Generate and send OTP
    from services.utils.security import generate_otp # Wait, generate_otp is in utils.security
    from utils.security import generate_otp
    
    otp_code = generate_otp()
    expires_at = (datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)).isoformat()
    
    supabase.table("otp_verifications").insert({
        "user_id": user['id'],
        "otp_type": otp_type,
        "otp_code": otp_code,
        "destination": identifier,
        "expires_at": expires_at
    }).execute()
    
    msg = ""
    if id_type == "email":
        await send_email_otp(identifier, otp_code, user['full_name'])
        msg = f"OTP sent to {identifier}"
    else:
        await send_sms_otp(identifier, otp_code)
        msg = f"OTP sent to {identifier}"
        
    return AuthResponse(
        success=True,
        message=msg,
        user={"id": user['id']}
    )

@router.post("/verify-login", response_model=AuthResponse)
async def verify_login(request: VerifyLoginOTPRequest):
    # Verify OTP
    await verify_otp(request.user_id, request.otp, request.otp_type)
    
    # Create Session
    session_token = await create_session(
        request.user_id, 
        request.device_fingerprint or "unknown", 
        request.remember_me
    )
    
    # Get user details
    user_data = await get_user_with_plan(request.user_id)
    
    return AuthResponse(
        success=True,
        message="Login successful",
        session_token=session_token,
        user=user_data['user'],
        plan=user_data['plan']
    )
    
@router.post("/resend-otp")
async def resend_otp_route(user_id: str, otp_type: str):
    return await resend_otp(user_id, otp_type)

@router.get("/me")
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing authentication token")
    
    token = auth_header.split(" ")[1]
    session = await verify_session_token(token)
    user_data = await get_user_with_plan(session['user_id'])
    return user_data
