from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Django application configuration for the authentication module.

    This is loaded by Django during startup and provides hooks
    for authentication app initialization.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    verbose_name = "Authentication"

    def ready(self) -> None:
        """
        Performs initialization tasks when Django starts.

        Note:
            Import any signal handlers here to avoid circular imports.
            Keep initialization lightweight to avoid slowing startup.
        """

        pass
