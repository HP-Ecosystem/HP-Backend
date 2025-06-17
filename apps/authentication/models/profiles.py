from django.db import models

from core.models import BaseProfileModel


class AgentProfile(BaseProfileModel):
    """
    Profile for agent users.

    Agents are property professionals who list and manage properties.
    """

    areas_of_expertise = models.JSONField(
        default=list,
        blank=True,
        help_text="List of property types or markets the agent specializes in (e.g., residential, commercial, luxury homes).",
    )

    class Meta:
        db_table = "agent_profiles"
        verbose_name = "Agent Profile"
        verbose_name_plural = "Agent Profiles"

    def __str__(self) -> str:
        return f"Agent Profile: {self.user.email}"


class VendorProfile(BaseProfileModel):
    """
    Profile for vendor users.

    Vendors sell household items and property-related products.
    This profile stores vendor-specific information like business
    details and inventory metrics.
    """

    class BusinessCategoryChoices(models.TextChoices):
        """Defines different category choices for a business."""

        FURNITURE = "FURNITURE", "Furniture"
        ELECTRONICS = "ELECTRONICS", "Electronics"
        APPLIANCES = "APPLIANCES", "Appliances"
        DECOR = "DECOR", "Home Decor"
        OTHER = "OTHER", "Other"

    business_category = models.CharField(
        max_length=32,
        choices=BusinessCategoryChoices.choices,
        default=BusinessCategoryChoices.FURNITURE,
        help_text="Category of business (e.g., furniture, electronics, appliances, decor, other).",
    )

    class Meta:
        db_table = "vendor_profiles"
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"

    def __str__(self) -> str:
        return f"Vendor Profile: {self.user.email}"


class ClientProfile(BaseProfileModel):
    """
    Profile for client users.

    Clients are users who browse and purchase properties or items.
    This profile stores client preferences and activity metrics.
    """

    search_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Client's property search preferences (e.g., property type, preferred locations, budget range).",
    )
    saved_search_filters = models.JSONField(
        default=list,
        blank=True,
        help_text="List of saved search filter criteria for quick access.",
    )

    class Meta:
        db_table = "client_profiles"
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

    def __str__(self) -> str:
        return f"Client Profile: {self.user.email}"
