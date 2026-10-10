from django.urls import path

from apps.platforms.views import PlatformListView

app_name = "platforms"

urlpatterns = [
    path("", PlatformListView.as_view(), name="platform-list"),
    path("", PlatformListView.as_view(), name="root"),
]
