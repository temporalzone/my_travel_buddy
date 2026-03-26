import jwt
import datetime
import os
from flask import request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()  # .env file se values load karo

SECRET_KEY = os.getenv("SECRET_KEY", "travelbuddy_secret_2025")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_reset_token(email):
    """Password reset token — 1 ghante mein expire"""
    payload = {
        "email": email,
        "type": "reset",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_reset_token(token):
    """Reset token verify karo"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "reset":
            return None
        return payload["email"]
    except:
        return None

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except:
        return None

def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    return verify_token(token)

def now():
    return datetime.datetime.utcnow().isoformat()

def send_reset_email(to_email, reset_token):
    """Send password reset email via SendGrid or Gmail fallback"""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Build correct reset link
    reset_link = f"{FRONTEND_URL}/my_travel_buddy/reset-password?token={reset_token}"

    html = f"""
    <div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:2rem;">
        <h2 style="color:#0EA5E9">Travel Buddy 🌍</h2>
        <p>Hi! You requested a password reset.</p>
        <p>Click below to reset your password:</p>
        <a href="{reset_link}"
           style="display:inline-block;background:#0EA5E9;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;margin:1rem 0;">
           Reset Password
        </a>
        <p style="color:#94A3B8;font-size:0.85rem;">
            This link expires in 1 hour.<br/>
            If you didn't request this, ignore this email.
        </p>
    </div>
    """

    # Try SendGrid first
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        email = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject="Travel Buddy — Reset Your Password",
            html_content=html
        )
        response = sg.send(email)
        print(f"Email sent via SendGrid to {to_email}")
        return True
    except Exception as e:
        print(f"SendGrid failed: {str(e)}")

    # Fallback to Gmail SMTP
    GMAIL = os.getenv("GMAIL_USER")
    GMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD")

    if not GMAIL or not GMAIL_PASS:
        print("No fallback email credentials (GMAIL_USER/GMAIL_APP_PASSWORD missing)")
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Travel Buddy — Reset Your Password"
    msg['From'] = GMAIL
    msg['To'] = to_email
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL, GMAIL_PASS)
        server.sendmail(GMAIL, to_email, msg.as_string())
        server.quit()
        print(f"Email sent via Gmail to {to_email}")
        return True
    except Exception as e:
        print(f"Gmail error: {str(e)}")
        return False
