"""Production settings for Housing & Properties project."""

from config.settings.base import *  # noqa
from config.settings.base import env

# Security Settings
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email configuration
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")

# Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.str("REDIS_URL"),
    }
}
