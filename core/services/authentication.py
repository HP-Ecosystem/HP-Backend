from datetime import UTC, datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import (
    ExpiredTokenError,
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from social_core.actions import do_auth
from social_core.utils import (
    partial_pipeline_data,
    user_is_active,
    user_is_authenticated,
)

if TYPE_CHECKING:
    from apps.authentication.models import User as UserClass

import re
import secrets
from typing import Any

from django.utils import timezone
from rest_framework.authentication import authenticate

from core.exceptions import BadRequestError, BaseAPIException
from core.logging import logger

User = get_user_model()


class AuthenticationService:
    """
    Service class for authentication operations.

    Handles:
        - user registration
        - authentication
        - token generation
        - password management
        - email verification.
    """

    def register_user(
        self, email: str, password: str, first_name: str, last_name: str, user_type: str
    ) -> tuple["UserClass", dict[str, str]]:
        """
        Registers a new user and generates authentication tokens.

        Args:
            email: The user's email address.
            password: The user's password.
            first_name: The user's first name.
            last_name: The user's last name.
            user_type: The type of user (e.g., client, agent).

        Returns:
            A tuple containing the created user object and a dict of access and refresh.
        """
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
            logger.exception(e)
            raise BaseAPIException(detail=f"User registration failed: {str(e)}") from e

    def login(self, email: str, password: str) -> tuple["UserClass", dict[str, str]]:
        """
        Authenticates a user and generates authentication tokens.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            A tuple containing the authenticated user object and a dict of access and refresh.

        Raises:
            ValidationError: If the email or password is invalid.
            BadRequestError: If the user account is deactivated or the email is not verified.
        """
        user = authenticate(username=email, password=password)
        if not user:
            raise ValidationError({"detail": "Invalid email or password"})

        if not user.is_active:
            raise BadRequestError(detail="Requested user account is deactivated")

        if not user.is_email_verified:
            raise BadRequestError(
                detail="Requested user email is not verified. Please verify your email"
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        tokens = self._generate_authentication_tokens(user)

        return user, tokens

    def verify_email(self, user_id: str, token: str) -> bool:
        """
        Verifies a user's email address using a token stored in the cache.

        Args:
            user_id: The ID of the user to verify.
            token: The verification token.

        Returns:
            True if the email was successfully verified.

        Raises:
            ValidationError: If the verification token is invalid or expired.
        """
        cache_key = f"email_verify_{user_id}"

        try:
            cached_id, cached_token = cache.get(cache_key)
        except Exception as e:
            logger.exception(e)
            raise ValidationError(
                {"detail": "Invalid or expired verification token"}
            ) from e

        user = User.objects.get(id=cached_id)

        if str(user.uuid) != user_id:
            raise ValidationError(
                {"detail": "Email verification failed. Invalid user uuid"}
            )

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        cache.delete(cache_key)

        return True

    def begin_social_authentication(
        self, request: Any, backend: str, user_type: str
    ) -> Any:
        """
        Begins the social authentication process.

        Args:
            request: The request object.
            backend: The social authentication backend to use.
            user_type: The type of user (e.g., client, agent).

        Returns:
            The result of the social authentication initiation.

        Raises:
            ValidationError: If the user type is invalid.
        """
        if user_type and user_type not in User.UserType.values:
            raise ValidationError({"detail": "Invalid user type"})

        request.session["user_type"] = user_type
        request.session.save()

        return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

    def complete_social_authentication(self, request, backend):
        """
        Completes the social authentication process.

        Handles both partial and full pipeline completion and generates tokens for the user.

        Args:
            request: The request object.
            backend: The social authentication backend.

        Returns:
            A tuple containing the authenticated user object and a dict of access and refresh.

        Raises:
            BadRequestError: If social authentication fails due to an invalid user object,
            inactive account, or other issues.
        """
        backend = request.backend
        user = request.user
        user_type = request.session.get("user_type", User.UserType.CLIENT)

        if "user_type" in request.session:
            del request.session["user_type"]

        is_user_authenticated = user_is_authenticated(user)
        user = user if is_user_authenticated else None

        partial = partial_pipeline_data(backend, user)
        if partial:
            user = backend.continue_pipeline(partial, user_type=user_type)
            backend.clean_partial_pipeline(partial.token)
        else:
            user = backend.complete(user=user, user_type=user_type)

        user_model = backend.strategy.storage.user.user_model()
        if user and not isinstance(user, user_model):
            raise BadRequestError(
                detail="Social authentication failed. Invalid User object."
            )

        if not user:
            raise BadRequestError(detail="Requested user account is inactive")

        if not user_is_active(user):
            raise BadRequestError(detail="This account has been deactivated")

        tokens = self._generate_authentication_tokens(user)

        return user, tokens

    def logout(self, user: "UserClass", access_token: str) -> str:
        """
        Logout a user by blacklisting their access token.

        Args:
            user: The user object to log out.
            access_token: The JWT access token to blacklist.

        Returns:
            A success message indicating the user has been logged out.

        Raises:
            ValidationError: If the access token is invalid or not provided.
        """
        from apps.authentication.models import BlacklistedToken

        token_expiry = self._validate_access_token(access_token)

        try:
            BlacklistedToken.objects.get_or_create(
                access=access_token, user=user, defaults={"expires_at": token_expiry}
            )
        except Exception as e:
            logger.exception(e)
            raise BaseAPIException(detail="User logout failed. Try again later.") from e

        return "User logout successful. Looking forward to your next visit!"

    def _validate_access_token(self, access_token: str) -> datetime:
        """
        Validates the JWT access token.

        Ensures the token is a valid string of standard length and not empty or whitespace.

        Args:
            access_token: The JWT access token to validate.

        Raises:
            ValidationError: If the access token is invalid.
        """
        if not access_token.strip():
            raise ValidationError({"detail": "Access token cannot be empty"})
        if len(access_token) < 10:
            raise ValidationError({"detail": "Access token is too short"})
        if len(access_token) > 500:
            raise ValidationError({"detail": "Access token is too long"})
        if not access_token.isprintable():
            raise ValidationError(
                {"detail": "Access token must be printable characters"}
            )
        if not access_token.strip():
            raise ValidationError(
                {"detail": "Access token cannot be empty or whitespace"}
            )

        try:
            access_token_obj = AccessToken(access_token)
            access_token_expiry = datetime.fromtimestamp(
                access_token_obj["exp"], tz=UTC
            )
        except (TokenError, ExpiredTokenError, InvalidToken) as e:
            raise ValidationError({"detail": "Invalid access token"}) from e

        return access_token_expiry

    def _validate_password(self, password: str) -> None:
        """
        Validates password strength.

        Ensures the password contains at least one uppercase letter, one lowercase letter,
        one digit, one special character, and no spaces.

        Raises:
            ValidationError: If the password does not meet the required criteria.
        """
        if " " in password:
            raise ValidationError({"password": "Password must not contain spaces."})

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

    def _generate_authentication_tokens(self, user: "UserClass") -> dict[str, str]:
        """
        Generates JWT tokens (access and refresh) for a user.

        Args:
            user: The user object to generate tokens for.

        Returns:
            A dictionary containing the access and refresh tokens.
        """
        refresh = RefreshToken.for_user(user)
        refresh["user_type"] = user.user_type
        refresh["email"] = user.email

        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    def _send_verification_email(self, user: "UserClass") -> None:
        """
        Sends an email verification link to the user.

        Args:
            user: The user object to send the verification email to.
        """
        from core.services import EmailService

        token = self._generate_verification_token()

        cache_key = f"email_verify_{str(user.uuid)}"

        expiry = getattr(settings, "VERIFICATION_TOKEN_EXPIRY", 15)
        cache.set(cache_key, (user.id, token), expiry * 60)

        try:
            EmailService.send_verification_email(user, token, expiry)
        except Exception as e:
            logger.exception(e)
            raise BaseAPIException(
                detail="Verification email failed to send. Try again later."
            ) from e

    def _generate_verification_token(self) -> str:
        """
        Generates a secure URL-safe verification token.

        Returns:
            A URL-safe string representing the verification token.
        """
        return secrets.token_urlsafe(32)
