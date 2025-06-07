"""v1 Authentication urls."""

from django.urls import path

from apps.authentication.views import EmailVerificationView, LoginView, RegisterView

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "verify-email/<str:user_id>/<str:verification_token>",
        EmailVerificationView.as_view(),
        name="verify-email",
    ),
]
