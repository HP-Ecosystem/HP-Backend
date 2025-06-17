import pytest
from django.contrib.auth import get_user_model

from apps.authentication.models import AgentProfile, ClientProfile, VendorProfile
from apps.authentication.tests.test_base import BaseTestCase, UserFactory
from core.exceptions import BadRequestError, ConflictError

User = get_user_model()


class UserManagerTest(BaseTestCase):
    """Test UserManager functionality."""

    def test_create_user_basic(self):
        """Test basic user creation through manager."""
        user = self.create_user(email="test@example.com")

        assert user.email == "test@example.com"
        assert user.check_password("Test@1234")
        assert user.user_type == "CLIENT"
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_create_user_with_all_fields(self):
        """Test user creation with all fields."""
        user = self.create_user(
            email="johndoe@example.com",
            user_type="AGENT",
            first_name="John",
            last_name="Doe",
            phone_number="+2348000001234",
        )

        assert user.email == "johndoe@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone_number == "+2348000001234"
        assert user.user_type == "AGENT"
        assert hasattr(user, "agent_profile")

    def test_create_user_email_normalization(self):
        """Test email normalization during user creation."""
        user = self.create_user(email="Test.User@EXAMPLE.COM")

        assert user.email == "Test.User@example.com"

    def test_create_user_without_password(self):
        """Test user creation without a password."""
        user = self.create_user(email="test@example.com", password=None)

        assert not user.has_usable_password()

    def test_create_user_without_email_raises_error(self):
        """Test creating user without email raises BadRequestError."""
        with pytest.raises(BadRequestError, match="Email address is required"):
            self.create_user(email="", password="Test@1234")

        with pytest.raises(BadRequestError, match="Email address is required"):
            self.create_user(email=None, password="Test@1234")

    def test_create_user_duplicate_email_raises_error(self):
        """Test creating user with duplicate email raises ConflictError."""
        self.create_user(email="duplicate@example.com", password="Test@1234")

        with pytest.raises(
            ConflictError,
            match="User with email 'duplicate@example.com' already exists",
        ):
            self.create_user(email="duplicate@example.com", password="Test@1234")

    def test_create_user_as_staff_raises_error(self):
        """Test regular user cannot be created as staff."""
        with pytest.raises(BadRequestError, match="Regular users cannot be staff"):
            self.create_user(
                email="staff@example.com", password="Test@1234", is_staff=True
            )

    def test_create_user_as_superuser_raises_error(self):
        """Test regular user cannot be created as superuser."""
        with pytest.raises(BadRequestError, match="Regular users cannot be superuser"):
            self.create_user(
                email="super@example.com", password="Test@1234", is_superuser=True
            )

    def test_create_superuser_basic(self):
        """Test superuser creation."""
        admin = self.create_user(
            email="admin@example.com",
            password="Admin@1234",
            user_creation_type="superuser",
        )

        assert admin.is_staff
        assert admin.is_superuser
        assert admin.user_type == "ADMIN"
        assert admin.is_email_verified
        assert admin.check_password("Admin@1234")

    def test_profile_creation_for_each_user_type(self):
        """Test correct profile is created for each user type."""
        # Client
        client = self.create_user(email="client@test.com", user_type="CLIENT")

        assert ClientProfile.objects.filter(user=client).exists()
        assert hasattr(client, "client_profile")

        # Agent
        agent = self.create_user(email="agent@test.com", user_type="AGENT")

        assert AgentProfile.objects.filter(user=agent).exists()
        assert hasattr(agent, "agent_profile")

        # Vendor
        vendor = self.create_user(
            email="vendor@test.com", password="Test@1234", user_type="VENDOR"
        )

        assert VendorProfile.objects.filter(user=vendor).exists()
        assert hasattr(vendor, "vendor_profile")

        # Admin (no profile)
        admin = self.create_user(
            email="admin@test.com",
            password="Admin@1234",
            user_creation_type="superuser",
        )

        assert not hasattr(admin, "client_profile")
        assert not hasattr(admin, "agent_profile")
        assert not hasattr(admin, "vendor_profile")


class UserQuerySetTest(BaseTestCase):
    """Test UserQuerySet functionality."""

    def setUp(self):
        super().setUp()

        # Create test users
        self.active_users = [UserFactory(is_active=True) for _ in range(3)]
        self.inactive_users = [UserFactory(is_active=False) for _ in range(2)]

    def test_active_queryset(self):
        """Test active() queryset method."""
        active = self.user_model.objects.active()

        assert active.count() == len(self.active_users)

        for user in self.active_users:
            assert user in active

        for user in self.inactive_users:
            assert user not in active

    def test_inactive_queryset(self):
        """Test inactive() queryset method."""
        inactive = self.user_model.objects.inactive()

        assert inactive.count() == len(self.inactive_users)

        for user in self.inactive_users:
            assert user in inactive

        for user in self.active_users:
            assert user not in inactive

    def test_search_empty_query(self):
        """Test search with empty query returns all users."""
        all_users = self.user_model.objects.all()

        # Empty string
        results = self.user_model.objects.search("")

        assert results.count() == all_users.count()

        # None
        results = self.user_model.objects.search(None)

        assert results.count() == all_users.count()

        # Whitespace
        results = self.user_model.objects.search("   ")

        assert results.count() == all_users.count()

    def test_search_by_email(self):
        """Test search by email."""
        user = UserFactory(email="unique.search@example.com")

        # Full email
        results = self.user_model.objects.search("unique.search@example.com")

        assert user in results

        # Partial email
        results = self.user_model.objects.search("unique.search")

        assert user in results

        # Domain
        results = self.user_model.objects.search("example.com")

        assert user in results

        # Case insensitive
        results = self.user_model.objects.search("UNIQUE.SEARCH")

        assert user in results

    def test_search_by_name(self):
        """Test search by first and last name."""
        user = UserFactory(first_name="Uniquefirst", last_name="Uniquelast")

        # First name
        results = self.user_model.objects.search("Uniquefirst")

        assert user in results

        # Last name
        results = self.user_model.objects.search("Uniquelast")

        assert user in results

        # Partial name
        results = self.user_model.objects.search("Unique")

        assert user in results

        # Case insensitive
        results = self.user_model.objects.search("uniquefirst")

        assert user in results

    def test_search_by_phone(self):
        """Test search by phone number."""
        user = UserFactory(phone_number="+2349123456789")

        # Full phone
        results = self.user_model.objects.search("+2349123456789")

        assert user in results

        # Partial phone
        results = self.user_model.objects.search("9123456789")

        assert user in results

        # With country code
        results = self.user_model.objects.search("234912")

        assert user in results

    def test_search_combined_fields(self):
        """Test search matches across multiple fields."""
        # Create user with 'test' in different fields
        user1 = UserFactory(email="test@example.com")
        user2 = UserFactory(first_name="Test")
        user3 = UserFactory(last_name="Testing")
        user4 = UserFactory(phone_number="+234test12345")  # Won't match

        results = self.user_model.objects.search("test")

        assert user1 in results
        assert user2 in results
        assert user3 in results
        assert user4 in results

    def test_manager_search_method(self):
        """Test search through manager returns same as queryset."""
        UserFactory(email="manager.search@test.com")

        queryset_results = self.user_model.objects.all().search("manager.search")
        manager_results = self.user_model.objects.search("manager.search")

        assert list(queryset_results) == list(manager_results)

    def test_chainable_querysets(self):
        """Test querysets can be chained."""
        active_user = UserFactory(email="chain@test.com", is_active=True)
        inactive_user = UserFactory(email="chain2@test.com", is_active=False)

        # Chain active() with search()
        results = self.user_model.objects.active().search("chain")

        assert active_user in results
        assert inactive_user not in results

        # Chain search() with active()
        results = self.user_model.objects.search("chain").active()

        assert active_user in results
        assert inactive_user not in results
