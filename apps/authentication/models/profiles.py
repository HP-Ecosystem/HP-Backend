"""
User profile models for type-sensitive data

This module implements the profile pattern to store additional data
specific to each user type.
"""

from django.core import validators
from django.db import models

from core.models import BaseModel


class AgentProfile(BaseModel):
    """
    Profile for agent users.

    Agents are property professionals who list and manage properties.
    This profile stores agent-specific information like licensing,
    specializations, and performance metrics."""

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="agent_profile",
        primary_key=True,
    )
    agency_name = models.CharField(max_length=100, blank=True)
    specializations = models.JSONField(
        default=list, help_text="List of specializations (e.g. residential, commercial)"
    )
    total_listings = models.PositiveIntegerField(default=0)
    total_sales = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[validators.MinValueValidator, validators.MaxValueValidator],
    )
    license_number = models.CharField(max_length=50, blank=True)
    is_license_verified = models.BooleanField(default=False)

    class Meta:
        """Meta options for AgentProfile."""

        db_table = "agent_profiles"
        verbose_name = "Agent Profile"
        verbose_name_plural = "Agent Profiles"

    def __str__(self) -> str:
        """String representation."""

        return f"Agent Profile: {self.user.email}"


class ClientProfile(BaseModel):
    """
    Profile for client users.

    Clients are users who browse and purchase properties or items.
    This profile stores client preferences and activity metrics.
    """

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="client_profile",
        primary_key=True,
    )
    property_preferences = models.JSONField(
        default=dict, help_text="Client's property preferences (type, location, budget)"
    )
    saved_searches = models.JSONField(
        default=list, help_text="List of saved search criteria"
    )
    total_purchases = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta options for ClientProfile."""

        db_table = "client_profiles"
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

    def __str__(self) -> str:
        """String representation."""

        return f"Client Profile: {self.user.email}"


class VendorProfile(BaseModel):
    """
    Profile for vendor users.

    Vendors sell household items and property-related products.
    This profile stores vendor-specific information like business
    details and inventory metrics.
    """

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="vendor_profile",
        primary_key=True,
    )
    business_name = models.CharField(max_length=100, blank=True)
    business_registration_no = models.CharField(
        max_length=50, blank=True, help_text="Business registration number"
    )
    business_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Type of business (e.g. furniture, electronics)",
    )
    business_address = models.TextField(blank=True)
    is_business_verified = models.BooleanField(default=False)

    class Meta:
        """Meta options for VendorProfile."""

        db_table = "vendor_profiles"
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"

    def __str__(self) -> str:
        """String representation."""

        return f"Vendor Profile: {self.user.email}"
