"""
Custom manager implementation for User model.

This module implements the repository pattern through Django managers,
encapsulating complex queries and providing a clean API for data access.
"""

from typing import TYPE_CHECKING

from django.contrib.auth import models as auth_models
from django.db import models

from core.exceptions import BadRequestError, ConflictError

if TYPE_CHECKING:
    from models import User
from core.models import BaseManager, BaseQuerySet


class UserQuerySet(BaseQuerySet):
    """Custom QuerySet for User model."""

    def search(self, query: str) -> "UserQuerySet":
        """Simple search for users by email, name, or phone number."""

        return self.filter(
            models.Q(email__icontains=query)
            | models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query)
            | models.Q(phone_number__icontains=query)
        )


class UserManager(auth_models.BaseUserManager, BaseManager):
    """Custom Manager for User model."""

    def _create_user(self, email: str, password: str, **extra_fields) -> "User":
        """Factory for user creation."""

        if not email:
            raise BadRequestError("Email address is required")

        email = self.normalize_email(email)

        if self.filter(email__iexact=email).exists():
            raise ConflictError(f"User with email '{email}' already exists")

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        self._create_profile(user)

        return user

    def create_user(
        self, email: str, password: str, user_type: str = "CLIENT", **extra_fields
    ) -> "User":
        """Create and save a regular user."""

        extra_fields.setdefault("user_type", user_type)

        if extra_fields.get("is_staff") is True:
            raise BadRequestError("Regular users cannot be staff")

        if extra_fields.get("is_superuser") is True:
            raise BadRequestError("Regular users cannot be superuser")

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "ADMIN")
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise BadRequestError("Superusers must have 'is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise BadRequestError("Superusers must have 'is_superuser=True'")

        return self._create_user(email, password, **extra_fields)

    def _create_profile(self, user: "User") -> None:
        """Create the appropriate profile for a user based on their type."""

        from models import AgentProfile, ClientProfile, VendorProfile

        profile_map = {
            "AGENT": AgentProfile,
            "VENDOR": VendorProfile,
            "CLIENT": ClientProfile,
        }

        profile_class = profile_map.get(user.user_type)
        if profile_class:
            profile_class.objects.create(user=user)

    def get_by_natural_key(self, username: str) -> "User":
        """Allow authentication by email."""

        return self.get(email__iexact=username)
