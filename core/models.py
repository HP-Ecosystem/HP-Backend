from typing import Any

from django.db import models
from django.utils import timezone


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
        Get public identifier for external use.

        Returns:
            String representation of UUID for API responses, URLs, etc.
        """
        if hasattr(self, "uuid"):
            return str(self.uuid)

    @property
    def internal_id(self) -> str:
        """
        Get internal identifier for database operations.

        Returns:
            Integer primary key for joins, foreign keys, etc.
        """
        return self.pk

    @classmethod
    def get_by_public_id(cls, public_id: str) -> BaseQuerySet:
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

    created = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="Timestamp for record creation"
    )
    updated = models.DateTimeField(
        auto_now=True, db_index=True, help_text="Timestamp for record updates"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Status indicating whether record is active or soft-deleted",
    )

    class Meta:
        """Meta options for BaseModel."""

        abstract = True
        ordering = ["-created"]
        indexes = [models.Index(fields=["created", "is_active"])]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to update timestamps."""
        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_active = True
        self.save(update_fields=["is_active"])

    def __str__(self):
        """String representation using public ID"""
        return f"{self.__class__.__name__}({self.public_id})"
