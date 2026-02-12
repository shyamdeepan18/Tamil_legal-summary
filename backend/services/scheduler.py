"""
Scheduler service for recurring tasks
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime
import contextlib

from database import SessionLocal
from models.auth_models import UserPlan, User
from utils.auth_utils import calculate_weekly_rollover

scheduler = AsyncIOScheduler()

async def weekly_rollover_task():
    """
    Weekly Pack Rollover Logic
    Runs every Sunday at 11:59 PM
    """
    print(f"[{datetime.utcnow()}] Starting weekly rollover task...")
    
    # Create a new session specifically for this task
    db = SessionLocal()
    try:
        # Get all active weekly packs
        active_packs = db.query(UserPlan).filter(
            UserPlan.plan_type == "weekly_pack",
            UserPlan.status == "active"
        ).all()
        
        count = 0
        for plan in active_packs:
            # Calculate rollover
            current_remaining = plan.documents_remaining
            # Default new allocation is 5
            new_allocation = 5
            
            # Use utility to calculate capped total (max 10)
            new_total = calculate_weekly_rollover(current_remaining, new_allocation)
            
            # Update plan
            plan.rollover_docs = current_remaining  # Track what rolled over
            plan.documents_remaining = new_total
            plan.documents_used = 0  # Reset usage for new week
            # Reset period start to now (ish)
            plan.period_start = datetime.utcnow().date()
            
            # TODO: Send notification email to user about rollover
            # user = plan.user
            # send_email(...)
            
            count += 1
        
        db.commit()
        print(f"[{datetime.utcnow()}] Weekly rollover completed for {count} users")
        
    except Exception as e:
        print(f"Error in weekly rollover: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start the scheduler"""
    # Schedule weekly rollover: Sunday 23:59
    # Using 'cron' trigger
    # scheduler.add_job(
    #     weekly_rollover_task,
    #     trigger='cron',
    #     day_of_week='sun',
    #     hour=23,
    #     minute=59,
    #     id='weekly_rollover',
    #     replace_existing=True
    # )
    
    scheduler.start()
    # print("✅ Scheduler started (Weekly rollover configured)")
    print("✅ Scheduler started")

def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown()
    print("🛑 Scheduler shutdown")
