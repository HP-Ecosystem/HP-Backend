from apps.authentication.views.authentication import (
    EmailVerificationView,
    LoginView,
    LogoutView,
    RegisterView,
    SocialAuthenticationBeginView,
    SocialAuthenticationCompleteView,
)

__all__ = [
    "RegisterView",
    "LoginView",
    "EmailVerificationView",
    "SocialAuthenticationBeginView",
    "SocialAuthenticationCompleteView",
    "LogoutView",
]
