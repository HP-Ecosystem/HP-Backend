"""API v1 URL configuration."""

from django.urls import include, path

urlpatterns = [
    path("authentication/", include("api.v1.urls.authentication")),
]
