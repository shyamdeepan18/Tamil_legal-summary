from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=13, max_length=13)
    full_name: str = Field(..., min_length=2, max_length=255)
    city: Optional[str] = None
    profession: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate Indian phone number format: +91XXXXXXXXXX"""
        if not re.match(r'^\+91[0-9]{10}$', v):
            raise ValueError('Phone must be in format +91XXXXXXXXXX')
        return v
    
    @field_validator('profession')
    @classmethod
    def validate_profession(cls, v):
        """Validate profession enum"""
        if v and v not in ['buyer', 'broker', 'lawyer', 'other']:
            raise ValueError('Invalid profession')
        return v

class UserCreate(UserBase):
    device_fingerprint: str

class UserResponse(BaseModel):
    id: str
    email: str
    phone: str
    full_name: str
    city: Optional[str]
    profession: Optional[str]
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
