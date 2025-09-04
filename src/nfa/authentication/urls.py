from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView,
    TOTPSetupView, TOTPVerifySetupView, TOTPDisableView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

    path("2fa/setup/", TOTPSetupView.as_view(), name="totp-setup"),
    path("2fa/verify-setup/", TOTPVerifySetupView.as_view(), name="totp-verify-setup"),
    path("2fa/disable/", TOTPDisableView.as_view(), name="totp-disable"),
]
