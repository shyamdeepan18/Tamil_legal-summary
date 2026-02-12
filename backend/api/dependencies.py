"""
API Dependencies
"""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.auth_models import UserSession, User, UserPlan

async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get current authentication user from session token
    """
    if not authorization:
        # For now, we might allow anonymous uploads for the demo/free tier
        # if the plan design permits, but the prompt implies strict checking for plan usage.
        # However, looking at the code, we want to allow "free_trial" flow.
        
        # If no header, return None (endpoint can decide if it requires auth)
        return None
        
    token = authorization.replace("Bearer ", "")
    
    # Find session
    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
        
    # Update last accessed
    session.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return session.user

async def get_active_plan(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active plan for the current user
    """
    if not user:
        return None
        
    plan = db.query(UserPlan).filter(
        UserPlan.user_id == user.id,
        UserPlan.status == "active"
    ).order_by(UserPlan.activated_at.desc()).first()
    
    return plan
