from typing import TYPE_CHECKING

from django.contrib.auth.models import BaseUserManager
from django.db import IntegrityError, models
from django.utils.translation import gettext_lazy as _

from core.exceptions import BadRequestError, ConflictError

if TYPE_CHECKING:
    from apps.authentication.models import User

from apps.authentication.models import AgentProfile, ClientProfile, VendorProfile
from core.models import BaseQuerySet


class UserQuerySet(BaseQuerySet):
    """Custom queryset for User model."""

    def search(self, query: str) -> "UserQuerySet":
        """
        Filters users based on a search query.

        The search is performed case-insensitively on the email, first name,
        last name, and phone number fields.

        Args:
            query: The search query string.

        Returns:
            A `UserQuerySet` containing the filtered users.

        :TODO: Implement optimizations for `icontains` query
        """
        if not query or query.strip() == "":
            return self.all()

        return self.filter(
            models.Q(email__icontains=query)
            | models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query)
            | models.Q(phone_number__icontains=query)
        )


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def get_queryset(self):
        """Returns a `UserQuerySet` object."""
        return UserQuerySet(model=self.model, using=self._db)

    def _create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        """
        Creates a new user.

        Args:
            email: The email address of the user.
            password: The user's password (optional).
            **extra_fields: Additional fields for the user model.

        Returns:
            The newly created `User` instance.

        Raises:
            BadRequestError: If the email address is not provided.
            ConflictError: If a user with the given email already exists.
        """
        if not email:
            raise BadRequestError(_("Email address is required"))

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password) if password else user.set_unusable_password()

        try:
            user.save(using=self._db)
            self._create_profile(user)

        except IntegrityError as e:
            if "email" in str(e):
                raise ConflictError(
                    _(f"User with email '{email}' already exists")
                ) from e

            raise ConflictError(_(str(e))) from e
        except Exception as e:
            raise e

        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        user_type: str = "CLIENT",
        **extra_fields,
    ) -> "User":
        """
        Creates a regular user.

        Args:
            email: The email address of the user.
            password: The user's password (optional).
            user_type: The type of user to create (default: 'CLIENT').
            **extra_fields: Additional fields for the user model.

        Returns:
            The newly created `User` instance.

        Raises:
            BadRequestError: If `is_staff` or `is_superuser` is True.
        """
        extra_fields.setdefault("user_type", user_type)

        if extra_fields.get("is_staff") is True:
            raise BadRequestError(_("Regular users cannot be staff"))

        if extra_fields.get("is_superuser") is True:
            raise BadRequestError(_("Regular users cannot be superuser"))

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        """
        Creates a superuser (staff and superuser).

        Args:
            email: The email address of the superuser.
            password: The superuser's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            The newly created `User` instance.

        Raises:
            BadRequestError: If `is_staff` or `is_superuser` is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "ADMIN")
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise BadRequestError(_("Superusers must have 'is_staff=True"))

        if extra_fields.get("is_superuser") is not True:
            raise BadRequestError(_("Superusers must have 'is_superuser=True'"))

        return self._create_user(email, password, **extra_fields)

    def _create_profile(self, user: "User") -> None:
        """
        Creates a user profile based on the user type.

        Args:
            user: The `User` instance for whom to create a profile.
        """
        profile_map = {
            "AGENT": AgentProfile,
            "VENDOR": VendorProfile,
            "CLIENT": ClientProfile,
        }

        profile_class = profile_map.get(user.user_type)
        if profile_class:
            profile_class.objects.create(user=user)

    def get_by_natural_key(self, username: str) -> "User":
        """
        Retrieves a user by their email address (natural key).

        Args:
            username: The email address of the user.

        Returns:
            The `User` instance matching the email address.
        """
        return self.get(email__iexact=username)

    def search(self, query: str) -> "UserQuerySet":
        """Search users with basic search."""
        return self.get_queryset().search(query)

    def active(self) -> BaseQuerySet:
        """Return only active users."""

        return self.get_queryset().active()

    def inactive(self) -> BaseQuerySet:
        """Return only inactive users."""

        return self.get_queryset().inactive()
