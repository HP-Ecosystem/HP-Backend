from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class CustomAuthenticationExtension(OpenApiAuthenticationExtension):
    """Custom authentication extension for OpenAPI schema generation."""

    target_class = (
        "apps.authentication.services.authentication.JWTBlacklistAuthentication"
    )
    name = "JWTBlacklistAuthentication"
    priority = -1

    def get_security_definition(self, auto_schema):
        """Return the security definition for the custom authentication."""

        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix="Bearer",
            bearer_format="JWT",
        )
