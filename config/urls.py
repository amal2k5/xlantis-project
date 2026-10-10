"""URL configuration for Xlantis RP Streamer & Content Directory project."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Simple health check endpoint returning service status."""
    return JsonResponse(
        {
            "status": "healthy",
            "service": "Xlantis RP Streamer & Content Directory API",
            "version": "1.0.0",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/v1/directory/", include("apps.directory.urls")),
    path("api/v1/platforms/", include("apps.platforms.urls")),
]
