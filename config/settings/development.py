"""Development settings for Housing & Properties project."""

from config.settings.base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar", "django_extensions"]  # noqa
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# CORS Settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

DATABASES = {
    "default": dj_database_url.config(  # noqa
        default="sqlite:///db.sqlite3",
        conn_max_age=env.int("CONN_MAX_AGE", default=600),  # noqa
        conn_health_checks=True,
    )
}

# Email Backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache config
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
