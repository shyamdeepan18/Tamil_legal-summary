"""
Database connection and initialization
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from typing import Generator

from models.auth_models import Base
from config import settings

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    settings.DATABASE_URL if hasattr(settings, 'DATABASE_URL') else "sqlite:///./tamil_ocr.db"
)

# Configure engine arguments based on DB type
engine_args = {
    "echo": settings.DEBUG
}

if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["poolclass"] = NullPool

# Create engine
engine = create_engine(DATABASE_URL, **engine_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database on import (for development)
if __name__ == "__main__":
    init_db()

from supabase_config import supabase, test_connection

