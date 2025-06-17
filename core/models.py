from django.db import models


class BaseQuerySet(models.QuerySet):
    """Base QuerySet with common filtering methods."""

    def active(self) -> "BaseQuerySet":
        """Return only active records."""
        return self.filter(is_active=True)

    def inactive(self) -> "BaseQuerySet":
        """Return only inactive records."""
        return self.filter(is_active=False)

    def with_prefetch(self, *fields) -> "BaseQuerySet":
        """
        Prefetch related fields for performance.

        Args:
            *fields: Field names to prefetch.

        Returns:
            QuerySet with prefetch_related applied.
        """
        return self.prefetch_related(*fields) if fields else self

    def with_select(self, *fields) -> "BaseQuerySet":
        """
        Select related fields for performance.

        Args:
            *fields: Field names to select.

        Returns:
            QuerySet with select_related applied.
        """
        return self.select_related(*fields) if fields else self


class BaseManager(models.Manager):
    """Base manager with common methods."""

    def get_queryset(self) -> BaseQuerySet:
        """Return the custom QuerySet."""

        return BaseQuerySet(self.model, using=self._db)

    def active(self) -> BaseQuerySet:
        """Return only active records."""

        return self.get_queryset().active()

    def inactive(self) -> BaseQuerySet:
        """Return only inactive records."""

        return self.get_queryset().inactive()


class BaseIDStrategyMixin:
    """Mixin to enforce consistent ID usage patterns."""

    @property
    def public_id(self) -> str:
        """
        Get public identifier for external use (UUID as string).

        Returns:
            String representation of UUID for API responses, URLs, etc.
        """
        return str(self.uuid) if hasattr(self, "uuid") else None

    @property
    def internal_id(self) -> str:
        """
        Get internal identifier for database operations.

        Returns:
            Integer primary key for joins, foreign keys, etc.
        """
        return self.pk

    @classmethod
    def get_by_public_id(cls, public_id: str) -> "BaseModel":
        """
        Retrieve instance by public UUID.

        Args:
            public_id: The UUID of the requested object.

        Returns:
            Model instance.

        Raises:
            DoesNotExist: If no object is not found with given UUID.
        """
        try:
            return cls.objects.get(uuid=public_id)
        except (ValueError, cls.DoesNotExist) as e:
            raise cls.DoesNotExist(
                f"No {cls.__name__} found with UUID: {public_id}"
            ) from e


class BaseModel(models.Model, BaseIDStrategyMixin):
    """Abstract base model with common fields and methods."""

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="Timestamp for record creation"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, help_text="Timestamp for record updates"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Status indicating whether record is active or soft-deleted",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at", "is_active"])]

    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_active = True
        self.save(update_fields=["is_active"])

    def __str__(self):
        return f"{self.__class__.__name__}({self.public_id})"


class BaseProfileModel(BaseModel):
    """
    Abstract base profile model for user profiles.

    Contains common fields like user reference and timestamps.
    Subclasses should define specific profile details.
    """

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="%(class)s_profile",
        primary_key=True,
    )
    business_name = models.CharField(
        max_length=100, blank=True, help_text="Name of business or agency or vendor"
    )
    business_address = models.TextField(
        blank=True, help_text="Location of the business"
    )
    business_registration_no = models.CharField(
        max_length=50, blank=True, help_text="Business registration number"
    )
    is_business_verified = models.BooleanField(
        default=False, help_text="Whether a business is verified"
    )
    license_number = models.CharField(
        max_length=50, blank=True, help_text="Professional license number"
    )
    is_license_verified = models.BooleanField(
        default=False, help_text="Whether an agent's credentials are verified"
    )

    class Meta:
        abstract = True
