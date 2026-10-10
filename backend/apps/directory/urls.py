from django.urls import path

from apps.directory.views import DirectoryRootView

app_name = "directory"

urlpatterns = [
    path("", DirectoryRootView.as_view(), name="root"),
]
