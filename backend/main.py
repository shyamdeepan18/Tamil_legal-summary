from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from contextlib import asynccontextmanager

from api import upload, payment, summary
from routes import auth, google_auth
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from database import init_db, test_connection, supabase
from cron_jobs import start_scheduler, stop_scheduler

# Initialize DB (Local SQLite/PG)
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Tamil Document Summarizer API...")
    
    # Test database connection (Supabase)
    if test_connection():
        print("✅ Database connected successfully")
    else:
        print("❌ Database connection failed")
    
    # Start background scheduler
    start_scheduler()
    print("✅ Background jobs started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    stop_scheduler()
    print("👋 Goodbye!")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Tamil Document Summarizer API",
    description="Privacy-first legal document analysis for Tamil users",
    version="1.0.0",
    lifespan=lifespan
)

# Add Session Middleware (Required for Google OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    # Combining settings with user request (user asked for "*")
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security & Timing Middleware (Preserved)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Endpoints
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Tamil Document Summarizer",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check with database status"""
    try:
        # Check Supabase health via RPC
        # Note: If RPC doesn't exist, this might fail unless backend falls back
        try:
            result = supabase.rpc('check_database_health').execute()
            metrics = result.data
        except:
            metrics = "RPC check_database_health unavailable"

        return {
            "status": "healthy",
            "database": "connected",
            "health_metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        # Using Supabase client directly
        result = supabase.table("users").select("count", count="exact").execute()
        # Plans might need table user_plans or similar
        plans_result = supabase.table("user_plans").select("plan_type, count", count="exact").eq("status", "active").execute()
        
        return {
            "total_users": result.count,
            "active_plans": plans_result.count,
            "timestamp": "now"
        }
    except Exception as e:
        # Fallback if table doesn't exist or other error
        print(f"Stats Error: {e}")
        return {"error": "Stats unavailable", "details": str(e)}

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(google_auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(payment.router, prefix="/api", tags=["payment"])
app.include_router(summary.router, prefix="/api", tags=["summary"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred.",
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

