import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    # Email (SMTP)
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    # App Settings
    APP_NAME = "Tamil Document Summarizer"
    APP_VERSION = "1.0.0"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    DEBUG = True
    
    # Rate Limiting
    RATE_LIMIT_UPLOAD = "10/minute"
    
    # Security
    SESSION_EXPIRE_DAYS = 7
    OTP_EXPIRE_MINUTES = 10
    OTP_MAX_ATTEMPTS = 3
    PASSWORD_RESET_EXPIRE_HOURS = 1
    MAX_ACCOUNTS_PER_DEVICE = 3
    
    # Email
    FROM_EMAIL = SMTP_EMAIL
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@yourdomain.com")
    
    # Razorpay (for later)
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    
    # OpenAI (for later)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

settings = Settings()
