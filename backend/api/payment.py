"""
Payment Integration - Razorpay payment processing
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import razorpay
import hmac
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from config import settings
from database import get_db
from models.auth_models import User, UserPlan, Order
from utils.auth_utils import get_plan_period_dates

router = APIRouter()

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


class CreateOrderRequest(BaseModel):
    amount: int  # in paise
    user_id: str
    upload_id: str
    plan: str  # "quick_check" or "standard"


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    upload_id: str


@router.post("/create-order")
async def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Create Razorpay order
    
    Returns order details for frontend to initiate payment
    """
    try:
        # Create order in Razorpay
        order = razorpay_client.order.create({
            'amount': request.amount,
            'currency': 'INR',
            'payment_capture': 1,  # Auto-capture
            'notes': {
                'user_id': request.user_id,
                'upload_id': request.upload_id,
                'product': 'document_summary',
                'plan': request.plan
            }
        })
        
        # Store order in database
        db_order = Order(
            user_id=request.user_id,
            razorpay_order_id=order['id'],
            upload_id=request.upload_id,
            amount=request.amount,
            plan_type=request.plan,
            status="created"
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return {
            'order_id': order['id'],
            'amount': request.amount,
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "order_creation_failed",
                "message": "Failed to create payment order. Please try again.",
                "tamil_message": "பணம் செலுத்தும் ஆர்டரை உருவாக்க முடியவில்லை"
            }
        )


@router.post("/verify-payment")
async def verify_payment(
    request: VerifyPaymentRequest, 
    db: Session = Depends(get_db)
):
    """
    Verify payment signature and activate plan
    """
    try:
        # 1. Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{request.razorpay_order_id}|{request.razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != request.razorpay_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # 2. Fetch Order details from Razorpay to identify User & Plan
        # (Secure way to ensure we give what was paid for)
        order = razorpay_client.order.fetch(request.razorpay_order_id)
        notes = order.get('notes', {})
        user_id = notes.get('user_id')
        plan_type = notes.get('plan')
        
        if not user_id or not plan_type:
            # Fallback if notes missing (shouldn't happen)
            # Maybe standard/one-off payment?
            pass

        # 3. Activate/Upgrade Plan
        if user_id and plan_type in ['quick_check', 'monthly_pack', 'pro_monthly', 'premium']:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # Find current active plan
                current_plan = db.query(UserPlan).filter(
                    UserPlan.user_id == user.id,
                    UserPlan.status == "active"
                ).first()

                remaining_docs = 0
                if current_plan:
                    # Upgrade Rule: Preserve remaining docs
                    remaining_docs = current_plan.documents_remaining
                    # Mark old plan as upgraded
                    current_plan.status = "upgraded"
                    current_plan.period_end = datetime.utcnow().date() # End it now
                
                # New Plan Limits
                limits = {
                    'quick_check': 1,
                    'monthly_pack': 15,
                    'pro_monthly': 30,
                    'premium': 200
                }
                new_limit = limits.get(plan_type, 0)
                
                # Calculate dates
                start_date, end_date = get_plan_period_dates(plan_type)
                
                # Create New Plan
                new_plan = UserPlan(
                    user_id=user.id,
                    plan_type=plan_type,
                    status="active",
                    documents_limit=new_limit,
                    documents_used=0,
                    # Add preserved docs to new limit for total available
                    documents_remaining=new_limit + remaining_docs,
                    amount_paid=order['amount'] / 100, # convert paise to rupees
                    period_start=start_date,
                    period_end=end_date,
                    activated_at=datetime.utcnow()
                )
                db.add(new_plan)
                db.commit()

        return {
            "status": "success",
            "message": "Plan activated successfully",
            "plan": plan_type,
            "upgrade": True
        }
    
    except Exception as e:
        print(f"Payment Verification Error: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")


@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """
    Handle Razorpay webhooks
    
    Events: payment.captured, payment.failed, etc.
    """
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    webhook_body = await request.body()
    
    # Verify webhook signature
    try:
        generated_signature = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            webhook_body,
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != webhook_signature:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        payload = await request.json()
        event = payload['event']
        
        if event == 'payment.failed':
            order_id = payload['payload']['payment']['entity']['order_id']
            # Update order status
            # We need a new DB session since this is a separate request
            db = next(get_db())
            try:
                order = db.query(Order).filter(Order.razorpay_order_id == order_id).first()
                if order:
                    order.status = "failed"
                    db.commit()
            except Exception as e:
                print(f"Error updating order status: {e}")
            finally:
                db.close()
        
        elif event == 'payment.captured':
            # Already handled in verify_payment, but good for redundancy
            pass
        
        return {"status": "ok"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Webhook processing failed")


@router.post("/refund")
async def initiate_refund(payment_id: str, amount: int, reason: str):
    """
    Initiate refund (for OCR failures)
    """
    try:
        refund = razorpay_client.payment.refund(payment_id, {
            'amount': amount,
            'notes': {'reason': reason}
        })
        
        # Update order status - NOT EASY without order_id or payment lookup via API
        # But we can try to find order by payment_id if we stored it (we didn't store payment_id in Order yet, only on Plan)
        # For MVP, we'll skip DB update here or would need to query Razorpay to get order_id
        
        # Notify user (Placeholder)
        print(f"Refund initiated for {payment_id}: {amount}")
        
        return {
            "status": "refunded",
            "refund_id": refund['id'],
            "message": "Refund initiated successfully",
            "tamil_message": "பணம் திரும்பப் பெறுதல் தொடங்கப்பட்டது"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "refund_failed",
                "message": "Failed to initiate refund. Please contact support.",
                "tamil_message": "பணம் திரும்பப் பெற முடியவில்லை"
            }
        )
