import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user: email is the login field and must be unique.
    is_verified becomes True only after OTP email verification.
    """
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    # Public profile fields
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    website_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("register", "Registration"),
        ("reset", "Password Reset"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="register")
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @staticmethod
    def generate_code():
        return f"{random.randint(0, 999999):06d}"

    def is_expired(self):
        expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 10)
        return timezone.now() > self.created_at + timedelta(minutes=expiry_minutes)

    def __str__(self):
        return f"{self.user.email} - {self.code} ({self.purpose})"
