import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def send_email_otp(email: str, otp: str, name: str):
    """Send OTP via Gmail SMTP"""
    
    subject = f"Your OTP: {otp}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6; 
                color: #333;
                max-width: 600px;
                margin: 0 auto;
            }}
            .container {{ 
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #667eea;
                margin: 0;
            }}
            .otp-box {{ 
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 8px;
                border-radius: 8px;
                margin: 30px 0;
                color: #667eea;
                border: 2px dashed #667eea;
            }}
            .info {{
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
            .footer {{ 
                font-size: 12px;
                color: #6c757d;
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <div class="header">
                    <h1>📄 {settings.APP_NAME}</h1>
                    <p>வணக்கம் {name}! 👋</p>
                </div>
                
                <p>Your verification code for {settings.APP_NAME}:</p>
                
                <div class="otp-box">{otp}</div>
                
                <div class="info">
                    <strong>⏰ Valid for {settings.OTP_EXPIRE_MINUTES} minutes</strong>
                </div>
                
                <p>If you didn't request this code, please ignore this email.</p>
                
                <div class="footer">
                    <p><strong>{settings.APP_NAME}</strong></p>
                    <p>Privacy-first legal document analysis</p>
                    <p>Your documents are auto-deleted after 15 minutes</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{settings.APP_NAME} <{settings.SMTP_EMAIL}>"
    msg['To'] = email
    msg['Subject'] = subject
    
    # Attach HTML
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Send email
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email OTP sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Email send failed: {e}")
        # For MVP/Development, don't crash if email fails, just log it. 
        # In production this might be different.
        raise HTTPException(500, f"Failed to send email: {str(e)}")


async def send_sms_otp(phone: str, otp: str):
    """
    Send OTP via SMS
    For MVP: Logs to console (add real SMS gateway later)
    """
    message = f"Your {settings.APP_NAME} OTP is: {otp}. Valid for {settings.OTP_EXPIRE_MINUTES} minutes. Do not share."
    
    # MVP: Log to console instead of sending SMS
    logger.info(f"📱 SMS to {phone}: {otp}")
    print(f"\n{'='*60}")
    print(f"📱 SMS OTP FOR TESTING")
    print(f"{'='*60}")
    print(f"Phone: {phone}")
    print(f"OTP: {otp}")
    print(f"Message: {message}")
    print(f"{'='*60}\n")
    
    # TODO: Add real SMS gateway
    # Options for India:
    # 1. MSG91: pip install msg91
    # 2. Fast2SMS: pip install fast2sms
    # 3. Twilio: pip install twilio
    
    return True


async def send_password_reset_email(email: str, reset_link: str, name: str):
    """Send password reset link via Gmail SMTP"""
    
    subject = "Reset Your Password"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2>Reset Your Password</h2>
        <p>Hi {name},</p>
        <p>You requested to reset your password for {settings.APP_NAME}.</p>
        
        <a href="{reset_link}" style="
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        ">Reset Password</a>
        
        <p><strong>This link expires in {settings.PASSWORD_RESET_EXPIRE_HOURS} hour.</strong></p>
        
        <p>If you didn't request this, please ignore this email.</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="font-size: 12px; color: #666;">
            {settings.APP_NAME}<br>
            Privacy-first legal document analysis
        </p>
    </body>
    </html>
    """
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{settings.APP_NAME} <{settings.SMTP_EMAIL}>"
    msg['To'] = email
    msg['Subject'] = subject
    
    # Attach HTML
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Send email
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Password reset email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Email send failed: {e}")
        raise HTTPException(500, f"Failed to send email: {str(e)}")
