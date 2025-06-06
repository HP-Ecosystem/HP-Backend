from apps.authentication.services.authentication import AuthenticationService
from apps.authentication.services.email import EmailService

authentication_service = AuthenticationService()
email_service = EmailService()

__all__ = [
    "authentication_service",
    "email_service",
]
