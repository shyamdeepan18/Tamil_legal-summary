"""
Authentication utility functions
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
import re


def generate_otp() -> str:
    """
    Generate 6-digit OTP
    
    Returns:
        str: 6-digit OTP code
    """
    return str(secrets.randbelow(1000000)).zfill(6)


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 with salt
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password in format "salt$hash"
    """
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        password_hash: Hashed password in format "salt$hash"
        
    Returns:
        bool: True if password matches
    """
    try:
        salt, hashed = password_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False


def generate_session_token() -> str:
    """
    Generate secure session token
    
    Returns:
        str: URL-safe session token
    """
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """
    Generate password reset token
    
    Returns:
        str: URL-safe reset token
    """
    return secrets.token_urlsafe(32)


def mask_email(email: str) -> str:
    """
    Mask email for privacy
    Example: ramesh@gmail.com -> r****h@gmail.com
    
    Args:
        email: Email address
        
    Returns:
        str: Masked email
    """
    try:
        username, domain = email.split('@')
        if len(username) <= 2:
            return f"{username[0]}*@{domain}"
        return f"{username[0]}{'*' * (len(username)-2)}{username[-1]}@{domain}"
    except:
        return email


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy
    Example: +919876543210 -> +91 98***43210
    
    Args:
        phone: Phone number in format +91XXXXXXXXXX
        
    Returns:
        str: Masked phone number
    """
    try:
        if phone.startswith('+91'):
            number = phone[3:]  # Remove +91
            return f"+91 {number[0:2]}***{number[-5:]}"
        return phone
    except:
        return phone


def validate_indian_phone(phone: str) -> bool:
    """
    Validate Indian phone number format
    
    Args:
        phone: Phone number
        
    Returns:
        bool: True if valid Indian phone number
    """
    pattern = r"^\+91[6-9]\d{9}$"
    return bool(re.match(pattern, phone))


def calculate_session_expiry(remember_me: bool = False) -> datetime:
    """
    Calculate session expiry time
    
    Args:
        remember_me: If True, session lasts 7 days, else 24 hours
        
    Returns:
        datetime: Expiry timestamp
    """
    if remember_me:
        return datetime.utcnow() + timedelta(days=7)
    else:
        return datetime.utcnow() + timedelta(hours=24)


def calculate_otp_expiry() -> datetime:
    """
    Calculate OTP expiry time (10 minutes)
    
    Returns:
        datetime: Expiry timestamp
    """
    return datetime.utcnow() + timedelta(minutes=10)


def calculate_reset_token_expiry() -> datetime:
    """
    Calculate password reset token expiry (1 hour)
    
    Returns:
        datetime: Expiry timestamp
    """
    return datetime.utcnow() + timedelta(hours=1)


def get_plan_period_dates(plan_type: str) -> Tuple[datetime, datetime]:
    """
    Calculate plan period start and end dates
    
    Args:
        plan_type: Plan type (free_trial, weekly_pack, pro_monthly, premium)
        
    Returns:
        Tuple[datetime, datetime]: (period_start, period_end)
    """
    now = datetime.utcnow()
    
    if plan_type == "free_trial":
        # Free trial never expires
        return now, now + timedelta(days=365 * 10)
    
    elif plan_type == "quick_check":
        # Quick Check: 24 hours validity
        return now, now + timedelta(hours=24)
    
    elif plan_type == "monthly_pack":
        # Monthly Pack: 30 Days fixed
        period_end = now + timedelta(days=30)
        return now, period_end
    
    elif plan_type in ["pro_monthly", "premium"]:
        # Monthly plans: Current month to next month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        period_end = next_month - timedelta(seconds=1)
        return now, period_end
    
    else:
        # Default: 30 days
        return now, now + timedelta(days=30)


def calculate_weekly_rollover(current_remaining: int, new_allocation: int = 5, max_rollover: int = 10) -> int:
    """
    Calculate weekly pack rollover documents
    
    Args:
        current_remaining: Current remaining documents
        new_allocation: New weekly allocation (default 5)
        max_rollover: Maximum accumulated documents (default 10)
        
    Returns:
        int: New total documents available
    """
    total = current_remaining + new_allocation
    return min(total, max_rollover)


def get_next_reset_date(plan_type: str) -> Optional[datetime]:
    """
    Get next reset date for plan
    
    Args:
        plan_type: Plan type
        
    Returns:
        Optional[datetime]: Next reset date or None for free_trial
    """
    now = datetime.utcnow()
    
    if plan_type in ["free_trial", "quick_check"]:
        return None
    
    elif plan_type == "monthly_pack":
        # No specific reset date like Sunday, it's just expiry
        return now + timedelta(days=30)
    
    elif plan_type in ["pro_monthly", "premium"]:
        # 1st of next month
        if now.month == 12:
            return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0)
        else:
            return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0)
    
    return None


def get_upgrade_options(current_plan: str) -> list:
    """
    Get available upgrade options for current plan
    Users can only upgrade, never downgrade
    
    Args:
        current_plan: Current plan type
        
    Returns:
        list: Available upgrade plan types
    """
    plan_hierarchy = {
        "free_trial": ["quick_check", "monthly_pack", "pro_monthly", "premium"],
        "quick_check": ["monthly_pack", "pro_monthly", "premium"],
        "monthly_pack": ["pro_monthly", "premium"],
        "pro_monthly": ["premium"],
        "premium": []  # Already on highest plan
    }
    
    return plan_hierarchy.get(current_plan, [])


def can_upgrade_to(current_plan: str, target_plan: str) -> bool:
    """
    Check if user can upgrade from current plan to target plan
    
    Args:
        current_plan: Current plan type
        target_plan: Target plan type
        
    Returns:
        bool: True if upgrade is allowed
    """
    upgrade_options = get_upgrade_options(current_plan)
    return target_plan in upgrade_options
