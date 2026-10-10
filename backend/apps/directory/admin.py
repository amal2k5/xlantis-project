"""Django admin registrations for Directory app."""

from django.contrib import admin
from django.db.models import Count, Prefetch, Q

from apps.directory.models import Category, Faction, Membership, Person
from apps.platforms.models import PlatformAccount


class CurrentMembershipFilter(admin.SimpleListFilter):
    """Filter memberships by active (current) vs ended (historical) status."""

    title = "membership status"
    parameter_name = "is_current"

    def lookups(self, request, model_admin):
        return [
            ("current", "Current members"),
            ("former", "Former members"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "current":
            return queryset.filter(ended_on__isnull=True)
        if self.value() == "former":
            return queryset.filter(ended_on__isnull=False)
        return queryset


class PersonMembershipInline(admin.TabularInline):
    """Inline for managing memberships on the Person admin form."""

    model = Membership
    extra = 0
    autocomplete_fields = ["faction"]
    fields = ["faction", "role", "started_on", "ended_on"]


class FactionMembershipInline(admin.TabularInline):
    """Inline for managing memberships on the Faction admin form."""

    model = Membership
    extra = 0
    autocomplete_fields = ["person"]
    fields = ["person", "role", "started_on", "ended_on"]


class PlatformAccountInline(admin.TabularInline):
    """Inline for managing platform accounts on the Person admin form."""

    model = PlatformAccount
    extra = 0
    autocomplete_fields = ["platform"]
    fields = ["platform", "handle", "external_id", "url", "is_verified"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""

    list_display = ["name", "slug", "is_active", "sort_order", "person_count"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["sort_order", "is_active"]
    ordering = ["sort_order", "name"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(person_count=Count("persons"))

    @admin.display(description="Persons", ordering="person_count")
    def person_count(self, obj):
        return getattr(obj, "person_count", 0)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Admin configuration for Person profile model."""

    list_display = [
        "display_name",
        "status",
        "is_featured",
        "get_current_gangs",
        "updated_at",
    ]
    list_filter = ["status", "is_featured", "categories"]
    search_fields = ["display_name", "slug", "bio"]
    prepopulated_fields = {"slug": ("display_name",)}
    filter_horizontal = ["categories"]
    inlines = [PersonMembershipInline, PlatformAccountInline]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "display_name",
                    "slug",
                    "status",
                    "is_featured",
                    "avatar_url",
                    "bio",
                ]
            },
        ),
        (
            "Categorization",
            {
                "fields": ["categories"],
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
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "categories",
                Prefetch(
                    "memberships",
                    queryset=Membership.objects.filter(ended_on__isnull=True).select_related(
                        "faction"
                    ),
                    to_attr="active_memberships",
                ),
            )
        )

    @admin.display(description="Current Gang(s)")
    def get_current_gangs(self, obj):
        active = getattr(obj, "active_memberships", None)
        if active is None:
            active = obj.memberships.filter(ended_on__isnull=True).select_related("faction")
        if not active:
            return "-"
        return ", ".join(m.faction.tag or m.faction.name for m in active)


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    """Admin configuration for Faction (gang/organization) model."""

    list_display = ["name", "tag", "status", "current_member_count", "updated_at"]
    list_filter = ["status"]
    search_fields = ["name", "tag", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FactionMembershipInline]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            None,
            {
                "fields": ["name", "slug", "tag", "status", "logo_url", "description"],
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
        return (
            super()
            .get_queryset(request)
            .annotate(
                active_member_count=Count(
                    "memberships",
                    filter=Q(memberships__ended_on__isnull=True),
                    distinct=True,
                )
            )
        )

    @admin.display(description="Active Members", ordering="active_member_count")
    def current_member_count(self, obj):
        return getattr(obj, "active_member_count", 0)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Admin configuration for Membership relationship model."""

    list_display = ["person", "faction", "role", "started_on", "ended_on", "is_current"]
    list_filter = [CurrentMembershipFilter, "role", "faction", "started_on", "ended_on"]
    search_fields = ["person__display_name", "faction__name", "faction__tag"]
    autocomplete_fields = ["person", "faction"]
    list_select_related = ["person", "faction"]
    date_hierarchy = "started_on"

    @admin.display(description="Current Member?", boolean=True)
    def is_current(self, obj):
        return obj.ended_on is None
