import uuid6
from authentication.managers import UserManager
from django.contrib.auth import models as auth_models
from django.db import models

from core.models import BaseModel


class User(auth_models.AbstractUser, BaseModel):
    """
    Custom user model for the Housing & Properties marketplace.

    Extends Django's AbstractUser to support multiple user types
    (clients, agents, vendors, admins) with type-specific attributes.
    """

    class UserType(models.TextChoices):
        """Defines the different user types in the system."""

        CLIENT = "CLIENT", "Client"
        AGENT = "AGENT", "Agent"
        VENDOR = "VENDOR", "Vendor"
        ADMIN = "ADMIN", "Administrator"

    username = None  # overriden
    email = models.EmailField(
        unique=True, db_index=True, help_text="User's email address"
    )
    uuid = models.UUIDField(
        default=uuid6.uuid7, editable=False, unique=True, help_text="Unique identifier"
    )
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        db_index=True,
        help_text="Type of user",
    )
    phone_number = models.CharField(
        max_length=20, blank=True, unique=True, help_text="User's phone number"
    )
    is_email_verified = models.BooleanField(
        default=False, help_text="Whether the email is verified"
    )
    is_phone_verified = models.BooleanField(
        default=False, help_text="Whether the phone number is verified"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """Metadata options for the User model."""

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["user_type", "is_active"]),
            models.Index(fields=["uuid"]),
        ]

    def __str__(self) -> str:
        """Returns the user's email address as the string representation."""
        return self.email

    @property
    def is_client(self) -> bool:
        """Returns True if the user is a client."""
        return self.user_type == self.UserType.CLIENT

    @property
    def is_agent(self) -> bool:
        """Returns True if the user is an agent."""
        return self.user_type == self.UserType.AGENT

    @property
    def is_vendor(self) -> bool:
        """Returns True if the user is a vendor."""
        return self.user_type == self.UserType.VENDOR

    @property
    def is_admin(self) -> bool:
        """Returns True if the user is an administrator."""
        return self.user_type == self.UserType.ADMIN

    @property
    def full_name(self) -> str:
        """Returns the user's full name or email if not available."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
