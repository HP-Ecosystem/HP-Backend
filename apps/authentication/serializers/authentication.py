from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.

    Validates and deserializes user registration data.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
        style={"input_type": "password"},
        help_text="Password (minimum 8 characters)",
    )
    user_type = serializers.ChoiceField(
        required=True, choices=User.UserType.choices, help_text="Type of user account"
    )
    first_name = serializers.CharField(
        required=True, max_length=30, help_text="User's first name"
    )
    last_name = serializers.CharField(
        required=True, max_length=30, help_text="User's last name"
    )


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates and deserializes user login data.
    """

    email = serializers.EmailField(required=True, help_text="User's email address")
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="User's password",
    )


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT token response.

    Serializes the JWT access and refresh tokens along with basic user information.
    Used for formatting the authentication service response.
    """

    access = serializers.CharField(read_only=True, help_text="JWT access token")
    refresh = serializers.CharField(read_only=True, help_text="JWT refresh token")
    user = serializers.SerializerMethodField(help_text="Basic user information")

    def get_user(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Returns user data for the token response.

        Formats the user information to include user ID, email, user type,
        first name, last name, and email verification status.

        Args:
            obj (dict[str, Any]): The object containing user data.

        Returns:
            _ (dict[str, Any]): A dictionary containing formatted user information.
        """
        user = obj.get("user")
        if user:
            return {
                "id": str(user.uuid),
                "email": user.email,
                "user_type": user.user_type,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_verified": user.is_email_verified,
            }
        return {}


class ErrorResponseExampleSerializer(serializers.Serializer):
    """
    Serializer for error response schema in OpenApi.

    Defines the structure of error responses for API documentation.
    """

    success = serializers.BooleanField(
        read_only=True, default=False, help_text="Indicates request success"
    )
    message = serializers.CharField(read_only=True, help_text="Error message")
    errors = serializers.DictField(
        read_only=True, help_text="Detailed error information"
    )
    status_code = serializers.IntegerField(read_only=True, help_text="HTTP status code")
