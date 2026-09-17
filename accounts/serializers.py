from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import OTP

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        # Inactive-for-login-purposes until OTP verified. We keep is_active=True
        # so Django admin login for staff still works, but gate API login on
        # is_verified instead.
        user.is_verified = False
        user.save()
        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs["email"].lower().strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        if user.is_verified:
            raise serializers.ValidationError("This account is already verified.")

        otp = OTP.objects.filter(
            user=user, code=attrs["code"], purpose="register", is_used=False
        ).order_by("-created_at").first()

        if not otp:
            raise serializers.ValidationError("Invalid verification code.")
        if otp.is_expired():
            raise serializers.ValidationError("This code has expired. Please request a new one.")

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower().strip()
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        if user.is_verified:
            raise serializers.ValidationError("This account is already verified.")
        return value


class LoginSerializer(TokenObtainPairSerializer):
    """
    Login with email + password. Blocks login until the account
    has completed OTP email verification.
    """
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        email = attrs.get("email").lower().strip()
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_verified:
            raise serializers.ValidationError("Please verify your email with the OTP sent to you before logging in.")

        data = super().validate(attrs)
        data["user"] = UserSerializer(user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for a user viewing/editing their OWN data, including
    their public profile (avatar, bio, social links)."""

    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_staff", "is_verified", "date_joined",
            "bio", "profile_picture",
            "website_url", "twitter_url", "instagram_url", "linkedin_url", "github_url",
        ]
        read_only_fields = ["id", "email", "is_staff", "is_verified", "date_joined"]


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer used by admins to view/update/delete ANY user."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name",
                  "is_staff", "is_active", "is_verified", "date_joined", "last_login",
                  "bio", "profile_picture"]
        read_only_fields = ["id", "date_joined", "last_login", "bio", "profile_picture"]
