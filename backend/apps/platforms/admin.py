"""Django admin registrations for Platforms app."""

from django.contrib import admin
from django.db.models import Count

from apps.platforms.models import Platform, PlatformAccount


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    """Admin configuration for Platform model."""

    list_display = [
        "name",
        "kind",
        "supports_live",
        "is_active",
        "sort_order",
        "account_count",
    ]
    list_filter = ["kind", "supports_live", "is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["sort_order", "is_active", "supports_live"]
    ordering = ["sort_order", "name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "slug",
                    "kind",
                    "supports_live",
                    "url_template",
                    "is_active",
                    "sort_order",
                ]
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(account_count=Count("accounts"))

    @admin.display(description="Accounts", ordering="account_count")
    def account_count(self, obj):
        return getattr(obj, "account_count", 0)


@admin.register(PlatformAccount)
class PlatformAccountAdmin(admin.ModelAdmin):
    """Admin configuration for PlatformAccount model."""

    list_display = [
        "person",
        "platform",
        "handle",
        "external_id",
        "is_verified",
        "updated_at",
    ]
    list_filter = ["platform", "is_verified"]
    search_fields = ["person__display_name", "handle", "external_id", "url"]
    autocomplete_fields = ["person", "platform"]
    list_select_related = ["person", "platform"]
    list_editable = ["is_verified"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "person",
                    "platform",
                    "handle",
                    "external_id",
                    "url",
                    "is_verified",
                    "notes",
                ]
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]
