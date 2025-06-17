from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


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
