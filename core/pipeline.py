from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from social_core.pipeline.user import USER_FIELDS

from core.exceptions import BadRequestError

User = get_user_model()


def create_user(
    backend, details: dict[str, Any], user=None, *args, **kwargs
) -> dict[str, Any]:
    """
    Custom pipeline step to create or update a social user.

    If a user already exists, verifies their email and updates last login.
    If not, creates a new user with the provided details and marks email as verified.

    Args:
        backend: The social auth backend in use.
        details: Dictionary of user details from the provider.
        user: Existing user instance, if any.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments, including user_type.

    Returns:
        dict: Contains the user instance and a boolean 'is_new' flag.

    Raises:
        BadRequestError: If the existing user's email is not verified.
    """
    if user:
        if not user.is_email_verified:
            raise BadRequestError(
                _("Requested user email is not verified. Please verify your email")
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return {"user": user, "is_new": False}

    user_type = kwargs.get("user_type")

    fields = {
        name: kwargs.get(name, details.get(name))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    }

    if not fields:
        return

    fields["is_email_verified"] = True
    fields["user_type"] = user_type
    user = User.objects.create_user(**fields)

    return {"user": user, "is_new": True}
