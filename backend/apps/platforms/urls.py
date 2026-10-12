from django.urls import path

from apps.platforms.views import (
    PlatformListView,
    PlatformLiveStatusListView,
)

app_name = "platforms"

urlpatterns = [
    path("", PlatformListView.as_view(), name="platform-list"),
    path("live-status/", PlatformLiveStatusListView.as_view(), name="live-status"),
]