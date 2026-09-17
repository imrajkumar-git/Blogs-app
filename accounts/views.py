from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import OTP
from .permissions import IsAdminStaff
from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    LoginSerializer,
    UserSerializer,
    AdminUserSerializer,
)
from .utils import create_and_send_otp

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Create a new (unverified) user and email them an OTP code."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        create_and_send_otp(user, purpose="register")
        return Response(
            {"detail": "Account created. Please check your email for the verification code.",
             "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    """Verify the OTP code and activate the account."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        otp = serializer.validated_data["otp"]

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return Response({"detail": "Email verified successfully. You can now log in."})


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"])
        create_and_send_otp(user, purpose="register")
        return Response({"detail": "A new verification code has been sent to your email."})


class LoginView(TokenObtainPairView):
    """Email + password login. Returns access & refresh tokens + user info."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    A logged-in user can view/update ONLY their own data — including
    uploading a profile picture (multipart/form-data) alongside the
    usual JSON fields.
    Regular users cannot escalate is_staff / is_verified through this
    endpoint (those fields are read_only on UserSerializer).
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Full CRUD over ALL users — admin (is_staff) only.
    Supports list, retrieve, partial_update (edit), destroy (delete).
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminStaff]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": "You cannot delete your own admin account from here."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
