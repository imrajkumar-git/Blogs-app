from django.core.mail import send_mail
from django.conf import settings

from .models import OTP


def create_and_send_otp(user, purpose="register"):
    """Generate a fresh OTP for the user and email it via Gmail SMTP."""
    otp = OTP.objects.create(user=user, code=OTP.generate_code(), purpose=purpose)

    subject = "Your verification code"
    if purpose == "reset":
        subject = "Your password reset code"

    message = (
        f"Hi {user.username},\n\n"
        f"Your one-time verification code is: {otp.code}\n"
        f"This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
        f"If you did not request this, you can safely ignore this email.\n"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return otp
