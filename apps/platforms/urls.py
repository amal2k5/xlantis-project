from django.urls import path

from apps.platforms.views import PlatformsRootView

app_name = "platforms"

urlpatterns = [
    path("", PlatformsRootView.as_view(), name="root"),
]
