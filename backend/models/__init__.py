"""
Database models for authentication and user management
"""

from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Date, ForeignKey, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User account table"""
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Optional, for password-based login
    
    # Profile information
    full_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    profession = Column(String(50), nullable=True)  # 'buyer', 'broker', 'lawyer', 'other'
    
    # Verification status
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Abuse prevention
    device_fingerprints = Column(JSON, default=list, nullable=False)  # Array of device IDs
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    ban_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    plans = relationship("UserPlan", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    otp_verifications = relationship("OTPVerification", back_populates="user", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="user")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class UserPlan(Base):
    """User subscription plans"""
    __tablename__ = "user_plans"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Plan details
    plan_type = Column(String(50), nullable=False)  # 'free_trial', 'monthly_pack', 'pro_monthly', 'premium'
    status = Column(String(20), default="active", nullable=False)  # 'active', 'expired', 'cancelled'
    
    # Document limits
    documents_limit = Column(Integer, nullable=False)
    documents_used = Column(Integer, default=0, nullable=False)
    documents_remaining = Column(Integer, nullable=False)
    
    # Rollover (for weekly pack)
    rollover_enabled = Column(Boolean, default=False, nullable=False)
    rollover_docs = Column(Integer, default=0, nullable=False)
    max_rollover = Column(Integer, default=10, nullable=False)
    
    # Billing
    amount_paid = Column(Float, nullable=True)
    payment_id = Column(String(255), nullable=True)
    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    
    # Period tracking
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    auto_renew = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    activated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="plans")
    
    # Indexes
    __table_args__ = (
        {"comment": "User subscription plans with rollover support"}
    )


class OTPVerification(Base):
    """OTP verification for signup and login"""
    __tablename__ = "otp_verifications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # OTP details
    otp_type = Column(String(20), nullable=False)  # 'email_signup', 'phone_signup', 'email_login', 'phone_login', 'password_reset'
    otp_code = Column(String(6), nullable=False)
    destination = Column(String(255), nullable=False)  # Email or phone number
    
    # Status
    is_verified = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    
    # Expiry
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="otp_verifications")
    
    # Indexes
    __table_args__ = (
        {"comment": "OTP verification records"}
    )


class UserSession(Base):
    """User login sessions"""
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session details
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    device_fingerprint = Column(String(255), nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Expiry (7 days for remember me, 24 hours default)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class PasswordReset(Base):
    """Password reset tokens"""
    __tablename__ = "password_resets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Reset token
    reset_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Status
    used = Column(Boolean, default=False, nullable=False)
    
    # Expiry (1 hour)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    used_at = Column(DateTime, nullable=True)


class Summary(Base):
    """Document summaries (existing table, adding user_id)"""
    __tablename__ = "summaries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User reference (NEW)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Plan type when processed (NEW)
    plan_type = Column(String(50), nullable=True)
    
    # Existing fields (placeholder - adjust based on your actual schema)
    upload_id = Column(String(255), unique=True, nullable=False)
    doc_type = Column(String(100), nullable=True)
    summary_text = Column(Text, nullable=True)
    red_flags = Column(JSON, default=list, nullable=True)
    health_score = Column(Integer, nullable=True)
    
    # Timestamps
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="summaries")


class Order(Base):
    """Payment orders"""
    __tablename__ = "orders"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Order details
    razorpay_order_id = Column(String(255), unique=True, nullable=False, index=True)
    upload_id = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False)  # in paise
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="created")  # created, paid, failed, refunded
    plan_type = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="orders")
