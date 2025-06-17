from core.services.authentication import AuthenticationService
from core.services.email import EmailService

authentication_service = AuthenticationService()
email_service = EmailService()

__all__ = [
    "authentication_service",
    "email_service",
]
