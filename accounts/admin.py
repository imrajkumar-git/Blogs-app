from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, OTP


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_staff", "is_active", "is_verified", "date_joined")
    list_filter = ("is_staff", "is_active", "is_verified")
    search_fields = ("email", "username")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Verification", {"fields": ("is_verified",)}),
        ("Profile", {"fields": ("bio", "profile_picture", "website_url",
                                 "twitter_url", "instagram_url", "linkedin_url", "github_url")}),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "purpose", "created_at", "is_used")
    list_filter = ("purpose", "is_used")
    search_fields = ("user__email", "code")


admin.site.register(User, UserAdmin)
