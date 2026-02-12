from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    city: Optional[str] = None
    profession: Optional[str] = None
    device_fingerprint: str

class VerifyOTPRequest(BaseModel):
    user_id: str
    email_otp: str = Field(..., min_length=6, max_length=6)
    phone_otp: str = Field(..., min_length=6, max_length=6)

class LoginRequest(BaseModel):
    identifier: str  # Email or phone
    login_type: str  # 'email' or 'phone'

class VerifyLoginOTPRequest(BaseModel):
    user_id: str
    otp: str = Field(..., min_length=6, max_length=6)
    otp_type: str  # 'email_login' or 'phone_login'
    remember_me: bool = False
    device_fingerprint: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class AuthResponse(BaseModel):
    success: bool
    message: str
    session_token: Optional[str] = None
    user: Optional[dict] = None
    plan: Optional[dict] = None
