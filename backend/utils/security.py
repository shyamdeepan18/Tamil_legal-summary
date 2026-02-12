import secrets
import hashlib
from datetime import datetime, timedelta

def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return str(secrets.randbelow(1000000)).zfill(6)

def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def generate_reset_token() -> str:
    """Generate password reset token"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hashed = password_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False

def mask_email(email: str) -> str:
    """Mask email: r****h@gmail.com"""
    username, domain = email.split('@')
    if len(username) <= 2:
        masked = username
    else:
        masked = f"{username[0]}{'*' * (len(username)-2)}{username[-1]}"
    return f"{masked}@{domain}"

def mask_phone(phone: str) -> str:
    """Mask phone: +91 98***12345"""
    return f"+91 {phone[3:5]}***{phone[-5:]}"
