"""
File upload endpoint with comprehensive validation
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Request, Header
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import uuid
import PyPDF2
import io
from typing import Optional

from config import settings
from services.ocr_service import OCRService
from services.classifier import DocumentClassifier
from services.preview_generator import PreviewGenerator

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

ocr_service = OCRService()
classifier = DocumentClassifier()
preview_generator = PreviewGenerator()


def validate_pdf_structure(file_content: bytes) -> bool:
    """Validate PDF structure to detect corruption"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        # Try to access first page
        if len(pdf_reader.pages) > 0:
            _ = pdf_reader.pages[0]
        return True
    except Exception:
        return False


def check_password_protected(file_content: bytes) -> bool:
    """Check if PDF is password protected"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        return pdf_reader.is_encrypted
    except Exception:
        return False


def unlock_pdf(file_content: bytes, password: str) -> tuple[bool, bytes]:
    """
    Try to unlock password-protected PDF
    
    Returns:
        (success: bool, unlocked_content: bytes)
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
        if not pdf_reader.is_encrypted:
            return True, file_content
        
        # Try to decrypt with password
        if pdf_reader.decrypt(password):
            # Create a new PDF without password
            pdf_writer = PyPDF2.PdfWriter()
            
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Write to bytes
            output = io.BytesIO()
            pdf_writer.write(output)
            unlocked_content = output.getvalue()
            
            return True, unlocked_content
        else:
            return False, file_content
    except Exception:
        return False, file_content


def get_page_count(file_content: bytes) -> int:
    """Get number of pages in PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        return len(pdf_reader.pages)
    except Exception:
        return 0


from api.dependencies import get_current_user, get_active_plan
from models.auth_models import User, UserPlan
from sqlalchemy.orm import Session
from database import get_db

@router.post("/upload")
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Upload and validate PDF document with Plan Checking
    """
    # 0. Check User Plan Limits (NEW)
    user = None
    if authorization:
        # Manual dependency call because of optional auth + Form data conflict risk with Depends
        from api.dependencies import get_current_user
        try:
            user = await get_current_user(authorization=authorization, db=db)
        except Exception:
            pass # Use free/anonymous limits if auth fails
    
    user_plan_type = "free" # Default
    
    if user:
        # Get active plan
        plan = db.query(UserPlan).filter(
            UserPlan.user_id == user.id,
            UserPlan.status == "active"
        ).order_by(UserPlan.activated_at.desc()).first()
        
        if plan:
            # Check expiry
            if plan.expires_at and plan.expires_at < datetime.utcnow():
                plan.status = "expired"
                db.commit()
                raise HTTPException(
                    status_code=403, 
                    detail={
                        "error": "plan_expired",
                        "message": "Your plan has expired. Please renew."
                    }
                )
            
            # Check remaining documents
            if plan.documents_remaining <= 0:
                 raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "limit_reached",
                        "message": f"{plan.plan_type} limit reached",
                        "current_plan": plan.plan_type,
                        "documents_used": plan.documents_used,
                        "documents_limit": plan.documents_limit,
                        "upgrade_suggestion": "pro_monthly" # Simple suggestion logic
                    }
                )
            
            user_plan_type = plan.plan_type
            
            # Decrement logic should arguably happen AFTER successful processing
            # But for this MVP we'll decrement here or we need to pass a callback
            # Let's decrement usage *after* we confirm validity (at the end of this function)
    
    # Step 1: Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_file_type",
                "message": "Only PDF files are supported",
                "tamil_message": "PDF கோப்புகள் மட்டுமே ஆதரிக்கப்படுகின்றன"
            }
        )
    
    # Map DB plan types to limit keys
    user_plan = user_plan_type
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Step 2: Check file size based on plan
    # Use mapping for new plan types
    limit_key = "free"
    if user_plan in ["quick_check", "monthly_pack", "pro_monthly", "premium"]:
        limit_key = "pro"
    elif user_plan == "free_trial":
        limit_key = "free"
        
    size_limits = {
        "free": settings.MAX_FILE_SIZE_FREE,
        "pro": settings.MAX_FILE_SIZE_PRO
    }
    
    max_size = size_limits.get(limit_key, settings.MAX_FILE_SIZE_FREE)
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "file_too_large",
                "message": f"File size exceeds {max_size_mb}MB limit for {user_plan} plan",
                "tamil_message": f"கோப்பு அளவு {max_size_mb}MB வரம்பை மீறுகிறது",
                "max_size_bytes": max_size,
                "actual_size_bytes": file_size,
                "upgrade_suggestion": "pro_monthly" if user_plan == "free" else "premium"
            }
        )
    
    # Step 3: Validate page count (before unlocking to save processing)
    page_count = get_page_count(file_content)
    
    if page_count == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_pdf",
                "message": "Could not read PDF pages. File may be corrupted.",
                "tamil_message": "PDF பக்கங்களை படிக்க முடியவில்லை"
            }
        )
    
    page_limits = {
        "free": settings.MAX_PAGES_FREE,
        "pro": settings.MAX_PAGES_PRO
    }
    
    max_pages = page_limits.get(limit_key, settings.MAX_PAGES_FREE)
    
    if page_count > max_pages:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "too_many_pages",
                "message": f"Document has {page_count} pages. {user_plan} plan supports up to {max_pages} pages.",
                "tamil_message": f"ஆவணத்தில் {page_count} பக்கங்கள் உள்ளன. {max_pages} பக்கங்கள் வரை மட்டுமே அனுமதிக்கப்படுகிறது",
                "page_count": page_count,
                "max_pages": max_pages,
                "upgrade_suggestion": "pro_monthly" if user_plan == "free" else "premium"
            }
        )
    
    # Step 4: Check for password protection
    is_password_protected = check_password_protected(file_content)
    
    if is_password_protected:
        if password is None:
            # Ask user for password
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "password_required",
                    "message": "This PDF is password protected. Please provide the password.",
                    "tamil_message": "இந்த PDF கடவுச்சொல் பாதுகாக்கப்பட்டுள்ளது. கடவுச்சொல்லை வழங்கவும்",
                    "requires_password": True
                }
            )
        else:
            # Try to unlock with provided password
            success, unlocked_content = unlock_pdf(file_content, password)
            
            if not success:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "incorrect_password",
                        "message": "Incorrect password. Please try again.",
                        "tamil_message": "தவறான கடவுச்சொல். மீண்டும் முயற்சிக்கவும்",
                        "requires_password": True
                    }
                )
            
            # Use unlocked content
            file_content = unlocked_content
    
    # Step 5: Validate PDF structure
    if not validate_pdf_structure(file_content):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "corrupted_pdf",
                "message": "PDF file appears to be corrupted. Please try re-scanning or re-saving the document.",
                "tamil_message": "PDF கோப்பு சேதமடைந்துள்ளது"
            }
        )
    
    # Generate unique upload ID
    upload_id = str(uuid.uuid4())
    
    # Save temporarily
    temp_path = os.path.join(settings.TEMP_DIR, f"{upload_id}.pdf")
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    try:
        # Step 6: Detect language
        language_info = ocr_service.detect_language(temp_path)
        
        if language_info["language"] == "unknown":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "unsupported_language",
                    "message": "Document language not supported. We support Tamil and English documents.",
                    "tamil_message": "ஆவண மொழி ஆதரிக்கப்படவில்லை"
                }
            )
        
        # Step 7: Run OCR
        ocr_result = await ocr_service.process_document(temp_path, language_info["language"])
        
        # Step 8: Check OCR quality
        quality_check = ocr_service.check_quality(ocr_result)
        
        if not quality_check["pass"]:
            # Delete temp file
            os.remove(temp_path)
            
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "poor_quality",
                    "message": "Could not extract clear text from document. Please upload a higher quality scan.",
                    "tamil_message": "ஆவணத்திலிருந்து தெளிவான உரையை பிரித்தெடுக்க முடியவில்லை",
                    "reason": quality_check["reason"],
                    "quality_score": quality_check.get("quality_score", 0),
                    "suggestions": [
                        "Rescan at 300 DPI or higher",
                        "Ensure good lighting",
                        "Flatten document before scanning",
                        "Avoid handwritten-only documents"
                    ]
                }
            )
        
        # Step 9: Classify document
        classification = classifier.classify(ocr_result["full_text"])
        
        if classification["type"] == "unsupported":
            # Delete temp file
            os.remove(temp_path)
            
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "unsupported_document_type",
                    "message": "This document type is not supported.",
                    "tamil_message": "இந்த ஆவண வகை ஆதரிக்கப்படவில்லை",
                    "supported_types": [
                        "Sale Deeds (விற்பனை பத்திரம்)",
                        "Agreements (ஒப்பந்தம்)",
                        "Encumbrance Certificates (EC)",
                        "Power of Attorney (POA)",
                        "Court Orders",
                        "Loan/Lease Documents"
                    ]
                }
            )
        
        # Decrement usage if user is on a plan
        if user and user_plan_type != "free":
            # We fetch plan again to be safe
            current_plan = db.query(UserPlan).filter(
                UserPlan.user_id == user.id,
                UserPlan.status == "active"
            ).first()
            
            if current_plan and current_plan.documents_remaining > 0:
                current_plan.documents_remaining -= 1
                current_plan.documents_used += 1
                db.commit()

        # Generate preview
        preview = preview_generator.generate(
            upload_id=upload_id,
            ocr_result=ocr_result,
            classification=classification,
            page_count=page_count,
            file_size=file_size
        )
        
        # Return preview for payment decision
        return JSONResponse(
            status_code=200,
            content={
                "upload_id": upload_id,
                "status": "ready_for_payment",
                "preview": preview,
                "pricing": {
                    "quick_check": {
                        "amount": settings.PRICE_QUICK_CHECK,
                        "amount_display": "₹49",
                        "features": ["Summary", "Red flags detection"]
                    },
                    "monthly_pack": {
                        "amount": 49900,
                        "amount_display": "₹499",
                        "features": ["15 Docs", "30 Days Validity", "Priority Support"]
                    }
                }
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "processing_failed",
                "message": "Failed to process document. Please try again.",
                "tamil_message": "ஆவணத்தை செயலாக்க முடியவில்லை"
            }
        )
