import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

User = get_user_model()


# =============== Factory Classes ===============
class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    email = Sequence(lambda n: f"user{n}@test.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    user_type = FuzzyChoice(["CLIENT", "AGENT", "VENDOR"])
    is_active = True
    is_email_verified = True
    phone_number = Sequence(lambda n: f"+234800000{n:04d}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override to use User manager's `create_user` or `create_superuser`.

        This method uses `user_creation_type` to determine how to create the user.

        Args:
            model_class: The model class to create the superuser for.
            *args: Positional arguments for the user creation.
            **kwargs: Keyword arguments for the user creation.
        Returns:
            The newly created superuser instance.
        """
        manager = cls._get_manager(model_class)

        user_creation_type = kwargs.pop("user_creation_type", "user")

        user = (
            manager.create_user(*args, **kwargs)
            if user_creation_type == "user"
            else (
                manager.create_superuser(*args, **kwargs)
                if user_creation_type == "superuser"
                else None
            )
        )

        return user


class AdminUserFActory(UserFactory):
    """Factory for creating test admin users."""

    user_type = "ADMIN"
    is_staff = True
    is_superuser = True


class AgentProfileFactory(DjangoModelFactory):
    """Factory for creating test agent profiles."""

    class Meta:
        model = "authentication.AgentProfile"

    user = SubFactory(UserFactory, user_type="AGENT")
    agency_name = Faker("company")
    license_number = Faker("bothify", text="AG-####-????")
    is_license_verified = False
    average_rating = Faker(
        "pydecimal", left_digits=1, right_digits=2, min_value=0.0, max_value=5.0
    )


class ClientProfileFactory(DjangoModelFactory):
    """Factory for creating test client profiles."""

    class Meta:
        model = "authentication.ClientProfile"

    user = SubFactory(UserFactory, user_type="CLIENT")
    property_preferences = Faker("pydict", nb_elements=3)
    saved_searches = Faker("pydict", nb_elements=2)


class VendorProfileFactory(DjangoModelFactory):
    """Factory for creating test vendor profiles."""

    class Meta:
        model = "authentication.VendorProfile"

    user = SubFactory(UserFactory, user_type="VENDOR")
    business_name = Faker("company")
    business_registration_no = Faker("bothify", text="BN-########")
    business_type = FuzzyChoice(["furniture", "electronics", "appliances"])
    business_address = Faker("address")


# =============== Test Classes ===============
class BaseTestCase(TestCase):
    """Base test case for authentication tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = get_user_model()

    def create_user(self, **kwargs):
        """
        Create a user with default values.

        Args:
            **kwargs: Keyword arguments for the user creation.
        Returns:
            The newly created user instance.
        """
        defaults = {
            "email": f"test_{timezone.now().timestamp()}@example.com",
            "password": "Test@1234",
            "user_type": "CLIENT",
            "is_email_verified": True,
            "user_creation_type": "user",
        }

        defaults.update(kwargs)

        return UserFactory(**defaults)


# =============== Fixtures ===============
@pytest.fixture
def user_factory():
    """Provide user factory for tests."""
    return UserFactory
