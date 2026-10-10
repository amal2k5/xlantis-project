from rest_framework.response import Response
from rest_framework.views import APIView


class DirectoryRootView(APIView):
    """Root endpoint for the Directory API."""

    def get(self, request):
        return Response(
            {
                "module": "directory",
                "status": "ready",
                "endpoints": {
                    "streamers": "/api/v1/directory/streamers/ (Phase 2)",
                    "characters": "/api/v1/directory/characters/ (Phase 2)",
                },
            }
        )
