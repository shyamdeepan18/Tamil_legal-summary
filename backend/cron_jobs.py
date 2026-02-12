from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from supabase_config import supabase
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Weekly rollover (Sundays at 11:59 PM IST)
# Weekly rollover (Sundays at 11:59 PM IST)
# @scheduler.scheduled_job('cron', day_of_week='sun', hour=23, minute=59, timezone='Asia/Kolkata')
# def weekly_rollover_job():
#     try:
#         # Check if user plans table exists/RPC exists before calling?
#         # Assuming RPCs are defined in Supabase
#         result = supabase.rpc('weekly_rollover').execute()
#         logger.info(f"✅ Weekly rollover completed: {result.data} users updated")
#     except Exception as e:
#         logger.error(f"❌ Weekly rollover failed: {e}")

# Monthly reset (1st of every month at 12:01 AM IST)
@scheduler.scheduled_job('cron', day=1, hour=0, minute=1, timezone='Asia/Kolkata')
def monthly_reset_job():
    try:
        result = supabase.rpc('monthly_reset').execute()
        logger.info(f"✅ Monthly reset completed: {result.data} users updated")
    except Exception as e:
        logger.error(f"❌ Monthly reset failed: {e}")

# Daily cleanup jobs (2 AM IST)
@scheduler.scheduled_job('cron', hour=2, minute=0, timezone='Asia/Kolkata')
def cleanup_jobs():
    try:
        # Cleanup OTPs
        supabase.rpc('delete_expired_otps').execute()
        
        # Cleanup sessions
        supabase.rpc('delete_expired_sessions').execute()
        
        # Cleanup password resets
        supabase.rpc('delete_expired_resets').execute()
        
        logger.info(f"✅ Daily cleanup completed")
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

# Database health check (every 6 hours)
@scheduler.scheduled_job('cron', hour='*/6', timezone='Asia/Kolkata')
def health_check_job():
    try:
        result = supabase.rpc('check_database_health').execute()
        warnings = [r for r in result.data if r.get('health_status') == 'WARNING']
        
        if warnings:
            logger.warning(f"⚠️ Database health warnings: {warnings}")
        else:
            logger.info("✅ Database health check passed")
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")

# Start scheduler
def start_scheduler():
    try:
        scheduler.start()
        logger.info("🚀 Scheduler started - Background jobs active")
    except Exception as e:
         logger.error(f"Failed to start scheduler: {e}")

# Stop scheduler
def stop_scheduler():
    scheduler.shutdown()
    logger.info("🛑 Scheduler stopped")
