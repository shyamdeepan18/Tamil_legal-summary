"""
Pydantic schemas for authentication and user management
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
import re


# ============================================
# SIGNUP & VERIFICATION SCHEMAS
# ============================================

class SignupRequest(BaseModel):
    """Signup request schema"""
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")  # Indian phone format
    city: Optional[str] = Field(None, max_length=100)
    profession: Optional[str] = Field(None, pattern=r"^(buyer|broker|lawyer|other)$")
    device_fingerprint: str = Field(..., min_length=10)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate Indian phone number"""
        if not re.match(r"^\+91[6-9]\d{9}$", v):
            raise ValueError("Invalid Indian phone number. Format: +91XXXXXXXXXX")
        return v


class SignupResponse(BaseModel):
    """Signup response schema"""
    success: bool
    message: str
    user_id: str
    email_masked: str
    phone_masked: str


class VerifyOTPRequest(BaseModel):
    """OTP verification request"""
    user_id: str
    email_otp: str = Field(..., pattern=r"^\d{6}$")
    phone_otp: str = Field(..., pattern=r"^\d{6}$")


class VerifyOTPResponse(BaseModel):
    """OTP verification response"""
    success: bool
    message: str
    session_token: str
    user: dict
    plan: dict


class ResendOTPRequest(BaseModel):
    """Resend OTP request"""
    user_id: str
    otp_type: str = Field(..., pattern=r"^(email_signup|phone_signup|email_login|phone_login)$")


# ============================================
# LOGIN SCHEMAS
# ============================================

class LoginEmailRequest(BaseModel):
    """Login with email request"""
    email: EmailStr


class LoginPhoneRequest(BaseModel):
    """Login with phone request"""
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")


class LoginOTPRequest(BaseModel):
    """Login OTP verification"""
    user_id: str
    otp: str = Field(..., pattern=r"^\d{6}$")
    otp_type: str = Field(..., pattern=r"^(email_login|phone_login)$")
    remember_me: bool = False
    device_fingerprint: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response"""
    success: bool
    session_token: str
    user: dict
    plan: dict


# ============================================
# PASSWORD MANAGEMENT SCHEMAS
# ============================================

class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain digit")
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request (logged in user)"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ============================================
# USER & PLAN SCHEMAS
# ============================================

class UserProfile(BaseModel):
    """User profile schema"""
    id: str
    email: str
    phone: str
    full_name: str
    city: Optional[str]
    profession: Optional[str]
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PlanInfo(BaseModel):
    """Plan information schema"""
    type: str
    documents_limit: int
    documents_used: int
    documents_remaining: int
    rollover_docs: int = 0
    period_start: date
    period_end: date
    next_reset: Optional[date]
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    user: dict
    plan: dict
    stats: dict
    recent_documents: List[dict]


# ============================================
# PLAN PURCHASE SCHEMAS
# ============================================

class PurchasePlanRequest(BaseModel):
    """Plan purchase request"""
    plan_type: str = Field(..., pattern=r"^(quick_check|monthly_pack|pro_monthly|premium)$")
    auto_renew: bool = False


class PurchasePlanResponse(BaseModel):
    """Plan purchase response"""
    success: bool
    order_id: str
    amount: int
    currency: str = "INR"
    razorpay_key_id: str


class UpgradePlanRequest(BaseModel):
    """Plan upgrade request"""
    new_plan_type: str = Field(..., pattern=r"^(quick_check|monthly_pack|pro_monthly|premium)$")


# ============================================
# SESSION SCHEMAS
# ============================================

class SessionInfo(BaseModel):
    """Session information"""
    session_token: str
    user_id: str
    expires_at: datetime
    device_fingerprint: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================
# ERROR RESPONSE SCHEMAS
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    message: str
    tamil_message: Optional[str] = None
    details: Optional[dict] = None


class ValidationError(BaseModel):
    """Validation error response"""
    success: bool = False
    error: str = "validation_error"
    message: str
    fields: dict
