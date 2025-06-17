from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request

from apps.authentication.models import BlacklistedToken
from core.logging import logger


class TokenBlacklistMiddleware(MiddlewareMixin):
    """
    Middleware to check if JWT tokens are blacklisted.

    This runs before the authentication backend.
    """

    def process_request(self, request: Request) -> None:
        """
        Check if the token in the request is blacklisted.

        If the token is blacklisted, clears the authorization header
        to prevent authentication.
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            if BlacklistedToken.is_blacklisted(token):
                request.META["HTTP_AUTHORIZATION"] = ""
                logger.warning(
                    f"Blacklisted token ({token[20:]}...) attempted to access: {str(request.path)}"
                )

        return None
