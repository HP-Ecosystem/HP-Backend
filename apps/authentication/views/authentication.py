from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.serializers import (
    TokenSerializer,
    UserRegistrationSerializer,
)
from apps.authentication.services import authentication_service
from core.utils.responses import StandardResponse


class RegisterView(APIView):
    """User registration endpoint."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: TokenSerializer},
        description="Register a new user account",
    )
    def post(self, request: Request) -> Response:
        """Handle user registration."""
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data
            user, tokens = authentication_service.register_user(**validated_data)
            response_data = {**tokens, "user": user}

            response_serializer = TokenSerializer(response_data)

            return StandardResponse.created(
                data=response_serializer.data,
                message="Registration successful. Please verify your email.",
            )
        except Exception as e:
            raise e
