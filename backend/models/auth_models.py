from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(datetime.now().timestamp())) # simplified ID for now, ideally uuid
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String, nullable=True) # Nullable for Google auth
    
    # Profile
    city = Column(String, nullable=True)
    profession = Column(String, nullable=True)
    
    # Auth Status
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Google Auth
    google_id = Column(String, nullable=True, unique=True)
    
    # Security
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    device_fingerprints = Column(JSON, default=list) # List of device hashes
    
    # Relationships
    plans = relationship("UserPlan", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    orders = relationship("Order", back_populates="user")

class UserPlan(Base):
    __tablename__ = "user_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    plan_type = Column(String) # free_trial, monthly_pack, pro_monthly, premium
    status = Column(String) # active, expired, upgraded
    
    # Limits & Usage
    documents_limit = Column(Integer)
    documents_used = Column(Integer, default=0)
    documents_remaining = Column(Integer)
    rollover_docs = Column(Integer, default=0) # Track carried over docs
    
    # Period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    activated_at = Column(DateTime, default=datetime.utcnow)
    
    # Payment
    amount_paid = Column(Float)
    
    user = relationship("User", back_populates="plans")

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    otp_type = Column(String) # email_signup, phone_signup, email_login, phone_login
    otp_code = Column(String)
    destination = Column(String) # email or phone
    
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    verified_at = Column(DateTime, nullable=True)

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    session_token = Column(String, unique=True, index=True)
    device_fingerprint = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="sessions")

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    reset_token = Column(String, unique=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(String, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    file_name = Column(String)
    file_size = Column(Integer)
    
    doc_type = Column(String)
    language = Column(String)
    
    # Analysis
    summary_content = Column(JSON) # Full summary
    red_flags = Column(JSON)
    health_score = Column(Integer)
    
    processed_at = Column(DateTime, default=datetime.utcnow)
    plan_type_used = Column(String, nullable=True) # Which plan covered this
    
    user = relationship("User", back_populates="summaries")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    razorpay_order_id = Column(String, unique=True, index=True, nullable=False)
    upload_id = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)  # in paise
    currency = Column(String, default="INR")
    status = Column(String, default="created")  # created, paid, failed, refunded
    plan_type = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
