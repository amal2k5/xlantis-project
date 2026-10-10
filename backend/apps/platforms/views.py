"""Views for the Platforms app."""

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from apps.platforms.models import Platform
from apps.platforms.serializers import PlatformSerializer


class PlatformListView(generics.ListAPIView):
    """Public read-only list of active external platforms.

    Excludes inactive platforms and internal credentials.
    Supports GET, HEAD, OPTIONS; rejects write methods with 405.
    """

    serializer_class = PlatformSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        params = self.request.query_params
        allowed = {"page", "page_size", "format"}
        unrecognized = set(params.keys()) - allowed
        if unrecognized:
            raise ValidationError(
                {"detail": f"Unrecognized query parameter(s): {', '.join(sorted(unrecognized))}."}
            )
        return Platform.objects.filter(is_active=True)


# Backwards compatibility alias for the root platform route
PlatformsRootView = PlatformListView
