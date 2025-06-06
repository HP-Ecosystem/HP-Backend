from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from .email import EmailService

if TYPE_CHECKING:
    from authentication.models import User as UserType
import re

User = get_user_model()


class AuthenticationService:
    """
    Service class for authentication operations.

    This service handles:
    - User registration with profile creation
    - Authentication and token generation
    - Password management
    - Email verification
    """

    @transaction.atomic
    def register_user(
        self, email: str, password: str, first_name: str, last_name: str, user_type: str
    ) -> tuple["UserType", dict[str, str]]:
        """Register a new user with appropriate profile creation."""

        self._validate_password(password)

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
            )

            tokens = self._generate_authentication_tokens(user)

            self._send_verification_email(user)

            return user, tokens

        except Exception as e:
            raise e

    def _validate_password(self, password: str) -> None:
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                {
                    "password": "Ensure this field contains at least one uppercase letter."
                }
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                {
                    "password": "Ensure this field contains at least one lowercase letter."
                }
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                {"password": "Ensure this field contains at least one digit."}
            )

        if not re.search(r"[^\w\s]", password):
            raise ValidationError(
                {
                    "password": "Ensure this field contains at least one special character."
                }
            )

    def _generate_authentication_tokens(self, user: "UserType") -> dict[str, str]:
        """Generate JWT tokens for users."""

        refresh = RefreshToken.for_user(user)
        refresh["user_type"] = user.user_type
        refresh["email"] = user.email

        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    def _send_verification_email(self, user: "UserType") -> None:
        """Send email verification link."""

        token = self._generate_verification_token()

        cache_key = f"email_verify_{str(user.uuid)}"

        expiry = getattr(settings, "VERIFICATION_TOKEN_EXPIRY", 15)
        cache.set(cache_key, token, expiry * 60)

        EmailService.send_verification_email(user, token, expiry)

    def _generate_verification_token(self) -> str:
        """Generate secure verification token."""

        import secrets

        return secrets.token_urlsafe(32)
