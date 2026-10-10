from rest_framework.response import Response
from rest_framework.views import APIView


class PlatformsRootView(APIView):
    """Root endpoint for the Platforms API."""

    def get(self, request):
        return Response(
            {
                "module": "platforms",
                "status": "ready",
                "supported_platforms": ["Twitch", "YouTube", "Kick"],
            }
        )
