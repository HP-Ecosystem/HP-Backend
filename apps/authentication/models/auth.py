from django.db import models
from django.utils import timezone

from core.models import BaseModel


class BlacklistedToken(BaseModel):
    """
    Model to store blacklisted JWT access tokens.

    Used in logout functionality to "invalidate" access tokens before expiry.
    """

    access = models.TextField(unique=True)
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="blacklisted_tokens",
        help_text="User associated with the blacklisted token",
    )
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "auth_blacklisted_tokens"
        indexes = [
            models.Index(fields=["access", "user"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"Token {self.access[:20]}... for {str(self.user)} (blacklisted at {self.created_at})"

    @classmethod
    def is_blacklisted(cls, access_token: str) -> bool:
        """Check if an access token is blacklisted."""
        return cls.objects.filter(access=access_token).exists()

    @classmethod
    def cleanup_expired(cls) -> None:
        """Delete expired blacklisted tokens."""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()
