import uuid6
from authentication.managers import UserManager
from django.contrib.auth import models as auth_models
from django.db import models

from core.models import BaseModel


class User(auth_models.AbstractUser, BaseModel):
    """
    Custom user model for Housing & Properties marketplace.

    This module implements a custom user model that extends Django's AbstractUser
    to support multiple user types (clients, agents, vendors, admins)
    with type-specific attributes and behaviors.
    """

    class UserType(models.TextChoices):
        """Enumeration of user types in the system."""

        CLIENT = "CLIENT", "Client"
        AGENT = "AGENT", "Agent"
        VENDOR = "VENDOR", "Vendor"
        ADMIN = "ADMIN", "Administrator"

    username = None  # overriden
    email = models.EmailField(unique=True, db_index=True)
    uuid = models.UUIDField(default=uuid6.uuid7, editable=False, unique=True)
    user_type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.CLIENT, db_index=True
    )
    phone_number = models.CharField(max_length=20, blank=True, unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """Meta options for User model."""

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["user_type", "is_active"]),
            models.Index(fields=["uuid"]),
        ]

    def __str__(self) -> str:
        """String representation of the user."""

        return self.email

    @property
    def is_client(self) -> bool:
        """Check if user is a client."""

        return self.user_type == self.UserType.CLIENT

    @property
    def is_agent(self) -> bool:
        """Check if user is a agent."""

        return self.user_type == self.UserType.AGENT

    @property
    def is_vendor(self) -> bool:
        """Check if user is a vendor."""

        return self.user_type == self.UserType.VENDOR

    @property
    def is_admin(self) -> bool:
        """Check if user is a admin."""

        return self.user_type == self.UserType.ADMIN

    @property
    def full_name(self) -> str:
        """Return the user's full name."""

        return f"{self.first_name} {self.last_name}".strip() or self.email
