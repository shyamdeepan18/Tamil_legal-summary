"""
Schemas package
"""

from .auth_schemas import (
    SignupRequest,
    SignupResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    ResendOTPRequest,
    LoginEmailRequest,
    LoginPhoneRequest,
    LoginOTPRequest,
    LoginResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserProfile,
    PlanInfo,
    DashboardStats,
    PurchasePlanRequest,
    PurchasePlanResponse,
    UpgradePlanRequest,
    SessionInfo,
    ErrorResponse,
    ValidationError
)

__all__ = [
    "SignupRequest",
    "SignupResponse",
    "VerifyOTPRequest",
    "VerifyOTPResponse",
    "ResendOTPRequest",
    "LoginEmailRequest",
    "LoginPhoneRequest",
    "LoginOTPRequest",
    "LoginResponse",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "ChangePasswordRequest",
    "UserProfile",
    "PlanInfo",
    "DashboardStats",
    "PurchasePlanRequest",
    "PurchasePlanResponse",
    "UpgradePlanRequest",
    "SessionInfo",
    "ErrorResponse",
    "ValidationError"
]
