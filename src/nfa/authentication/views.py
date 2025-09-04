from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django_otp.plugins.otp_totp.models import TOTPDevice
import base64, os, pyotp

from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    TOTPSetupSerializer, TOTPVerifySetupSerializer, TOTPDisableSerializer,
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        otp = serializer.validated_data.get("otp")

        has_2fa = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        if has_2fa:
            if not otp:
                return Response(
                    {"detail": "Two-factor authentication required.", "2fa_required": True},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
            if not device.verify_token(otp):
                return Response({"detail": "Invalid email, password or OTP."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"detail": f"Token error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Incorrect old password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."})

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(reverse("password-reset-confirm"))
            reset_link = f"{reset_url}?uid={uid}&token={token}"

            subject = "Password Reset Request"
            message = f"Click the link to reset your password: {reset_link}"
            EmailMessage(subject=subject, body=message,
                        from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email]).send(fail_silently=False)

        return Response({"detail": "If an account exists, a reset link has been sent."})

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully."})

class TOTPSetupView(generics.GenericAPIView):
    serializer_class = TOTPSetupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        if not device:
            secret_b32 = pyotp.random_base32()
            key_bytes = base64.b32decode(secret_b32, casefold=True)
            device = TOTPDevice.objects.create(
                user=user,
                name="default",
                key=key_bytes,
                step=30,
                digits=6,
                tolerance=1,
                confirmed=False,
            )
        else:
            secret_b32 = base64.b32encode(device.key).decode("utf-8")

        issuer = os.getenv("TOTP_ISSUER", "NFA")
        otpauth_url = pyotp.totp.TOTP(secret_b32).provisioning_uri(name=user.email, issuer_name=issuer)
        return Response({"secret": secret_b32, "otpauth_url": otpauth_url})

class TOTPVerifySetupView(generics.GenericAPIView):
    serializer_class = TOTPVerifySetupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data["otp"]
        device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
        if not device or not device.verify_token(otp):
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        device.confirmed = True
        device.save(update_fields=["confirmed"])
        return Response({"detail": "Two-factor authentication enabled."})

class TOTPDisableView(generics.GenericAPIView):
    serializer_class = TOTPDisableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data.get("confirm", False):
            return Response({"detail": "Confirmation required."}, status=status.HTTP_400_BAD_REQUEST)

        TOTPDevice.objects.filter(user=request.user).delete()
        return Response({"detail": "Two-factor authentication disabled."})
