"""Base models and managers for Housing & Properties."""

from typing import Any

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Abstract base model with common fields and methods."""

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        """Meta options for BaseModel."""

        abstract = True
        ordering = ["-created"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to update timestamps."""

        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        """Soft delete the record."""

        self.is_active = False
        self.save()

    def restore(self) -> None:
        """Restore a soft-deleted record."""

        self.is_active = True
        self.save()


class BaseQuerySet(models.QuerySet):
    """Base QuerySet with common filtering methods."""

    def active(self) -> "BaseQuerySet":
        """Return only active records."""

        return self.filter(is_active=True)

    def inactive(self) -> "BaseQuerySet":
        """Return only inactive records."""

        return self.filter(is_active=False)


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
