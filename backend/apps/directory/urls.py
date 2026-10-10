from django.urls import path

from apps.directory.views import (
    CategoryListView,
    DirectoryRootView,
    FactionDetailView,
    FactionListView,
    PersonDetailView,
    PersonListView,
)

app_name = "directory"

urlpatterns = [
    path("", DirectoryRootView.as_view(), name="root"),
    path("persons/", PersonListView.as_view(), name="person-list"),
    path("persons/<slug:slug>/", PersonDetailView.as_view(), name="person-detail"),
    path("people/", PersonListView.as_view(), name="people-list"),
    path("people/<slug:slug>/", PersonDetailView.as_view(), name="people-detail"),
    path("factions/", FactionListView.as_view(), name="faction-list"),
    path("factions/<slug:slug>/", FactionDetailView.as_view(), name="faction-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
]
