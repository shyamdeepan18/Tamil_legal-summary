import re
from typing import Tuple

def is_email(identifier: str) -> bool:
    """Check if string is valid email"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, identifier))

def is_phone(identifier: str) -> bool:
    """Check if string is valid phone"""
    phone_pattern = r'^\+91[0-9]{10}$'
    return bool(re.match(phone_pattern, identifier))

def detect_identifier_type(identifier: str) -> Tuple[str, str]:
    """
    Detect if identifier is email or phone
    Returns: (type, identifier)
    """
    if is_email(identifier):
        return ('email', identifier)
    elif is_phone(identifier):
        return ('phone', identifier)
    else:
        raise ValueError("Invalid email or phone format")
