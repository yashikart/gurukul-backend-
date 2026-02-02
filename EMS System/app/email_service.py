"""
Email service for sending password setup emails.
"""
import secrets
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import HTTPException, status
from app.config import settings
from app.models import User, PasswordToken


# Email configuration
# Auto-fix: If MAIL_FROM doesn't match MAIL_USERNAME, use MAIL_USERNAME (required for Gmail)
mail_from = settings.MAIL_FROM
if settings.MAIL_USERNAME and settings.MAIL_FROM != settings.MAIL_USERNAME:
    print(f"[EMAIL WARNING] MAIL_FROM ({settings.MAIL_FROM}) doesn't match MAIL_USERNAME ({settings.MAIL_USERNAME})")
    print(f"[EMAIL WARNING] Using MAIL_USERNAME as MAIL_FROM for Gmail compatibility")
    mail_from = settings.MAIL_USERNAME

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=mail_from,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=None,
)


async def send_password_setup_email(
    db: Session,
    user: User,
    password_token: PasswordToken
) -> bool:
    """
    Send password setup email to the user.
    
    Args:
        db: Database session
        user: User object
        password_token: PasswordToken object
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create password setup link
        setup_link = f"{settings.FRONTEND_URL}/set-password?token={password_token.token}"
        
        # Email content
        subject = "Set Your Password - School Management System"
        body = f"""
        Hello {user.name},
        
        You have been invited to join the School Management System as an Administrator.
        
        Please set your password by clicking on the following link:
        {setup_link}
        
        This link will expire in {settings.PASSWORD_TOKEN_EXPIRE_MINUTES} minutes.
        
        If you did not request this invitation, please ignore this email.
        
        Best regards,
        School Management System
        """
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            body=body,
            subtype=MessageType.plain,
        )
        
        # Send email with timeout
        fm = FastMail(conf)
        try:
            await asyncio.wait_for(fm.send_message(message), timeout=30.0)
            print(f"[EMAIL] Successfully sent password setup email to {user.email}")
            print(f"[EMAIL] Setup link: {setup_link}")
            return True
        except asyncio.TimeoutError:
            print(f"[EMAIL ERROR] Timeout: SMTP connection to {settings.MAIL_SERVER} timed out after 30 seconds")
            print(f"[EMAIL ERROR] This usually means the SMTP server is unreachable or blocking the connection")
            print(f"[EMAIL ERROR] Gmail SMTP often blocks connections from cloud providers like Render")
            print(f"[EMAIL ERROR] Consider using SendGrid, Mailgun, or AWS SES instead of Gmail SMTP")
            return False
        except Exception as smtp_error:
            # Log SMTP-specific errors (e.g., authentication failures, sender not verified)
            print(f"[EMAIL ERROR] SMTP error when sending to {user.email}")
            print(f"[EMAIL ERROR] Error type: {type(smtp_error).__name__}")
            print(f"[EMAIL ERROR] Error message: {str(smtp_error)}")
            print(f"[EMAIL ERROR] SMTP Server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
            print(f"[EMAIL ERROR] Sender (MAIL_FROM): {mail_from}")
            print(f"[EMAIL ERROR] Recipient: {user.email}")
            
            # Check for common Brevo/SendGrid errors
            error_str = str(smtp_error).lower()
            if "sender" in error_str and ("not verified" in error_str or "unauthorized" in error_str):
                print(f"[EMAIL ERROR] SENDER EMAIL NOT VERIFIED: The sender email ({mail_from}) must be verified in your email service (Brevo/SendGrid)")
                print(f"[EMAIL ERROR] Action: Go to your email service dashboard and verify the sender email address")
            elif "authentication" in error_str or "invalid credentials" in error_str:
                print(f"[EMAIL ERROR] AUTHENTICATION FAILED: Check MAIL_USERNAME and MAIL_PASSWORD")
            elif "550" in error_str or "553" in error_str:
                print(f"[EMAIL ERROR] EMAIL REJECTED: The email service rejected the message (likely sender not verified)")
            
            import traceback
            print(f"[EMAIL ERROR] Full traceback:")
            traceback.print_exc()
            return False
        
    except Exception as e:
        # Log error with full details
        print(f"[EMAIL ERROR] Failed to send email to {user.email}")
        print(f"[EMAIL ERROR] Error type: {type(e).__name__}")
        print(f"[EMAIL ERROR] Error message: {str(e)}")
        import traceback
        print(f"[EMAIL ERROR] Traceback:")
        traceback.print_exc()
        return False


async def send_login_credentials_email(
    db: Session,
    user: User,
    password: str,
    role: str
) -> bool:
    """
    Send login credentials email to newly created users (Teachers, Students, Parents).
    Includes generated password and reset password link.
    
    Args:
        db: Database session
        user: User object
        password: Plain text password (will be sent in email)
        role: User role (TEACHER, STUDENT, PARENT)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Generate password reset token
        password_token = generate_password_token(db, user.id)
        
        role_display = {
            "TEACHER": "Teacher",
            "STUDENT": "Student",
            "PARENT": "Parent"
        }.get(role, role)
        
        login_url = f"{settings.FRONTEND_URL}/login"
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={password_token.token}"
        
        # Email content
        subject = f"Your {role_display} Account Credentials - School Management System"
        body = f"""
Hello {user.name},

Your {role_display} account has been created in the School Management System.

═══════════════════════════════════════════════════════════
YOUR LOGIN CREDENTIALS:
═══════════════════════════════════════════════════════════

Email Address: {user.email}
Password: {password}

═══════════════════════════════════════════════════════════

Please login at: {login_url}

IMPORTANT SECURITY INFORMATION:
- You can use the generated password above to log in immediately
- The password contains only letters and numbers (no special characters)
- We strongly recommend changing your password to something more memorable
- Click the link below to reset your password to a new one of your choice

RESET PASSWORD LINK:
{reset_link}

This reset link will expire in {settings.PASSWORD_TOKEN_EXPIRE_MINUTES} minutes.

IMPORTANT: When resetting your password, you will need to provide:
- Your CURRENT password (the generated password above)
- Your NEW password (choose a new one)

TROUBLESHOOTING:
- Make sure you copy the password exactly as shown (case-sensitive)
- Check for any extra spaces before or after the password
- If login fails, use the reset password link above

SECURITY NOTES:
- Do not share your password with anyone
- Keep your credentials secure
- Change your password regularly

If you did not expect this account, please contact your school administrator immediately.

Best regards,
School Management System
        """
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            body=body,
            subtype=MessageType.plain,
        )
        
        # Send email with timeout
        fm = FastMail(conf)
        try:
            await asyncio.wait_for(fm.send_message(message), timeout=30.0)
            print(f"[EMAIL] Successfully sent login credentials to {user.email}")
            print(f"[EMAIL] Reset link: {reset_link}")
            return True
        except asyncio.TimeoutError:
            print(f"[EMAIL ERROR] Timeout: SMTP connection to {settings.MAIL_SERVER} timed out after 30 seconds")
            print(f"[EMAIL ERROR] This usually means the SMTP server is unreachable or blocking the connection")
            print(f"[EMAIL ERROR] Gmail SMTP often blocks connections from cloud providers like Render")
            print(f"[EMAIL ERROR] Consider using SendGrid, Mailgun, or AWS SES instead of Gmail SMTP")
            return False
        except Exception as smtp_error:
            # Log SMTP-specific errors
            print(f"[EMAIL ERROR] SMTP error when sending login credentials to {user.email}")
            print(f"[EMAIL ERROR] Error type: {type(smtp_error).__name__}")
            print(f"[EMAIL ERROR] Error message: {str(smtp_error)}")
            error_str = str(smtp_error).lower()
            if "sender" in error_str and ("not verified" in error_str or "unauthorized" in error_str):
                print(f"[EMAIL ERROR] SENDER EMAIL NOT VERIFIED: The sender email ({mail_from}) must be verified in your email service")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        # Log error with full details
        print(f"[EMAIL ERROR] Failed to send login credentials to {user.email}")
        print(f"[EMAIL ERROR] Error type: {type(e).__name__}")
        print(f"[EMAIL ERROR] Error message: {str(e)}")
        import traceback
        print(f"[EMAIL ERROR] Traceback:")
        traceback.print_exc()
        return False


def generate_password_token(db: Session, user_id: int) -> PasswordToken:
    """
    Generate a secure, unique token for password setup.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        PasswordToken: Created password token
    """
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_TOKEN_EXPIRE_MINUTES)
    
    # Create password token
    password_token = PasswordToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        is_used=False
    )
    
    db.add(password_token)
    db.commit()
    db.refresh(password_token)
    
    return password_token


def validate_password_token(db: Session, token: str) -> PasswordToken:
    """
    Validate a password setup token.
    
    Args:
        db: Database session
        token: Token string
        
    Returns:
        PasswordToken: Valid password token
        
    Raises:
        HTTPException: If token is invalid, expired, or already used
    """
    password_token = db.query(PasswordToken).filter(PasswordToken.token == token).first()
    
    if not password_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
    if password_token.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been used"
        )
    
    if password_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    
    return password_token


def mark_token_as_used(db: Session, password_token: PasswordToken) -> None:
    """
    Mark a password token as used.
    
    Args:
        db: Database session
        password_token: PasswordToken object
    """
    password_token.is_used = True
    db.commit()


async def send_password_reset_email(
    db: Session,
    user: User,
    password_token: PasswordToken
) -> bool:
    """
    Send password reset email to the user.
    
    Args:
        db: Database session
        user: User object
        password_token: PasswordToken object
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create password reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={password_token.token}"
        
        # Email content
        subject = "Reset Your Password - School Management System"
        body = f"""
Hello {user.name},

You have requested to reset your password for your {user.role.value} account.

Please reset your password by clicking on the following link:
{reset_link}

IMPORTANT: You will need to provide:
- Your CURRENT password (old password)
- Your NEW password

This link will expire in {settings.PASSWORD_TOKEN_EXPIRE_MINUTES} minutes.

If you did not request this password reset, please ignore this email and your password will remain unchanged.

Best regards,
School Management System
        """
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            body=body,
            subtype=MessageType.plain,
        )
        
        # Send email with timeout
        fm = FastMail(conf)
        try:
            await asyncio.wait_for(fm.send_message(message), timeout=30.0)
            print(f"[EMAIL] Successfully sent password reset email to {user.email}")
            print(f"[EMAIL] Reset link: {reset_link}")
            return True
        except asyncio.TimeoutError:
            print(f"[EMAIL ERROR] Timeout: SMTP connection to {settings.MAIL_SERVER} timed out after 30 seconds")
            print(f"[EMAIL ERROR] This usually means the SMTP server is unreachable or blocking the connection")
            print(f"[EMAIL ERROR] Gmail SMTP often blocks connections from cloud providers like Render")
            print(f"[EMAIL ERROR] Consider using SendGrid, Mailgun, or AWS SES instead of Gmail SMTP")
            return False
        except Exception as smtp_error:
            # Log SMTP-specific errors
            print(f"[EMAIL ERROR] SMTP error when sending password reset to {user.email}")
            print(f"[EMAIL ERROR] Error type: {type(smtp_error).__name__}")
            print(f"[EMAIL ERROR] Error message: {str(smtp_error)}")
            error_str = str(smtp_error).lower()
            if "sender" in error_str and ("not verified" in error_str or "unauthorized" in error_str):
                print(f"[EMAIL ERROR] SENDER EMAIL NOT VERIFIED: The sender email ({mail_from}) must be verified in your email service")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        # Log error with full details
        print(f"[EMAIL ERROR] Failed to send password reset email to {user.email}")
        print(f"[EMAIL ERROR] Error type: {type(e).__name__}")
        print(f"[EMAIL ERROR] Error message: {str(e)}")
        import traceback
        print(f"[EMAIL ERROR] Traceback:")
        traceback.print_exc()
        return False


async def send_school_admin_credentials_email(
    db: Session,
    user: User,
    password: str,
    password_token: PasswordToken,
    school_name: str
) -> bool:
    """
    Send school admin credentials email with generated password and reset link.
    
    Args:
        db: Database session
        user: User object (school admin)
        password: Plain text generated password
        password_token: PasswordToken object for reset link
        school_name: Name of the school
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create password reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={password_token.token}"
        login_url = f"{settings.FRONTEND_URL}/login"
        
        # Email content
        subject = f"Your School Admin Account Credentials - {school_name}"
        body = f"""
Hello {user.name},

Your school "{school_name}" has been created in the School Management System, and you have been set up as the School Administrator.

═══════════════════════════════════════════════════════════
YOUR LOGIN CREDENTIALS:
═══════════════════════════════════════════════════════════

Email Address: {user.email}
Password: {password}

═══════════════════════════════════════════════════════════

Please login at: {login_url}

IMPORTANT SECURITY INFORMATION:
- You can use the generated password above to log in immediately
- The password contains only letters and numbers (no special characters)
- We strongly recommend changing your password to something more memorable
- Click the link below to reset your password to a new one of your choice

RESET PASSWORD LINK:
{reset_link}

This reset link will expire in {settings.PASSWORD_TOKEN_EXPIRE_MINUTES} minutes.

IMPORTANT: When resetting your password, you will need to provide:
- Your CURRENT password (the generated password above)
- Your NEW password (choose a new one)

TROUBLESHOOTING:
- Make sure you copy the password exactly as shown (case-sensitive)
- Check for any extra spaces before or after the password
- If login fails, use the reset password link above

SECURITY NOTES:
- Do not share your password with anyone
- Keep your credentials secure
- Change your password regularly

If you did not expect this account, please contact the system administrator immediately.

Best regards,
School Management System
        """
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            body=body,
            subtype=MessageType.plain,
        )
        
        # Send email with timeout
        fm = FastMail(conf)
        try:
            await asyncio.wait_for(fm.send_message(message), timeout=30.0)
            print(f"[EMAIL] Successfully sent school admin credentials to {user.email}")
            print(f"[EMAIL] Reset link: {reset_link}")
            return True
        except asyncio.TimeoutError:
            print(f"[EMAIL ERROR] Timeout: SMTP connection to {settings.MAIL_SERVER} timed out after 30 seconds")
            print(f"[EMAIL ERROR] This usually means the SMTP server is unreachable or blocking the connection")
            print(f"[EMAIL ERROR] Gmail SMTP often blocks connections from cloud providers like Render")
            print(f"[EMAIL ERROR] Consider using SendGrid, Mailgun, or AWS SES instead of Gmail SMTP")
            return False
        except Exception as smtp_error:
            # Log SMTP-specific errors
            print(f"[EMAIL ERROR] SMTP error when sending school admin credentials to {user.email}")
            print(f"[EMAIL ERROR] Error type: {type(smtp_error).__name__}")
            print(f"[EMAIL ERROR] Error message: {str(smtp_error)}")
            error_str = str(smtp_error).lower()
            if "sender" in error_str and ("not verified" in error_str or "unauthorized" in error_str):
                print(f"[EMAIL ERROR] SENDER EMAIL NOT VERIFIED: The sender email ({mail_from}) must be verified in your email service")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        # Log error with full details
        print(f"[EMAIL ERROR] Failed to send school admin credentials to {user.email}")
        print(f"[EMAIL ERROR] Error type: {type(e).__name__}")
        print(f"[EMAIL ERROR] Error message: {str(e)}")
        import traceback
        print(f"[EMAIL ERROR] Traceback:")
        traceback.print_exc()
        return False