from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

if TYPE_CHECKING:
    from authentication.models import User


class EmailService:
    """Service class for sending emails."""

    @staticmethod
    def send_email(
        subject: str,
        message: str,
        recipient_list: list[str],
        html_message: str | None = None,
        from_email: str | None = None,
    ) -> int:
        """Send and return the number of emails sent."""

        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        return send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def send_template_email(
        subject: str,
        template_name: str,
        context: dict[str, Any],
        recipient_list: list[str],
        from_email: str | None = None,
    ) -> int:
        """Send an email using a template and return the number of emails sent."""

        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        # Render HTML and text versions
        html_content = render_to_string(f"{template_name}.html", context)
        text_content = strip_tags(html_content)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")

        return email.send()

    @staticmethod
    def send_verification_email(
        user: "User", verification_token: str, token_expiry: int
    ) -> int:
        """Send email verification email."""

        verification_url = reverse(
            "authentication:verify-email",
            kwargs={
                "user_id": str(user.uuid),
                "verification_token": verification_token,
            },
        )

        context = {
            "user": user,
            "expiry_minutes": token_expiry,
            "verification_url": verification_url,
            "from_domain": settings.FROM_DOMAIN,
        }

        return EmailService.send_template_email(
            subject="Verify your email address",
            template_name="verify_email",
            context=context,
            recipient_list=[user.email],
        )
