"""Views for the Directory app."""

from django.db.models import Count, Prefetch, Q
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.directory.models import (
    Category,
    Faction,
    Membership,
    Person,
    PersonStatus,
)
from apps.directory.serializers import (
    PUBLIC_FACTION_STATUSES,
    CategorySerializer,
    FactionDetailSerializer,
    FactionListSerializer,
    PersonDetailSerializer,
    PersonListSerializer,
)
from apps.platforms.models import PlatformAccount


class StandardResultsSetPagination(PageNumberPagination):
    """Configurable pagination supporting ?page= and ?page_size= parameters."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


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


class PersonListView(generics.ListAPIView):
    """Public read-only list of published directory profiles.

    Supports:
    - Search by display_name and bio: `?search=<term>`
    - Filter by active category slug: `?category=<category-slug>`
    - Filter by public faction slug: `?faction=<faction-slug>`
    - Filter by featured status: `?featured=true` or `?featured=false`
    - Pagination: `?page=<number>&page_size=<size>`

    Query parameters are strictly validated; invalid values or unrecognized
    parameters return HTTP 400 Bad Request.
    Write methods return HTTP 405 Method Not Allowed.
    """

    serializer_class = PersonListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        params = self.request.query_params
        allowed = {"search", "category", "faction", "featured", "page", "page_size", "format"}
        unrecognized = set(params.keys()) - allowed
        if unrecognized:
            raise ValidationError(
                {"detail": f"Unrecognized query parameter(s): {', '.join(sorted(unrecognized))}."}
            )

        queryset = Person.objects.filter(status=PersonStatus.PUBLISHED).prefetch_related(
            Prefetch("categories", queryset=Category.objects.filter(is_active=True))
        )

        # 1. Search by display_name and bio
        search = params.get("search")
        if search:
            search = search.strip()
            if search:
                queryset = queryset.filter(
                    Q(display_name__icontains=search) | Q(bio__icontains=search)
                )

        # 2. Filter by category slug
        if "category" in params:
            category_slug = (params.get("category") or "").strip()
            if (
                not category_slug
                or not Category.objects.filter(slug=category_slug, is_active=True).exists()
            ):
                raise ValidationError(
                    {
                        "category": [
                            f"Invalid category '{category_slug}'. "
                            "Category does not exist or is inactive."
                        ]
                    }
                )
            queryset = queryset.filter(categories__slug=category_slug)

        # 3. Filter by public faction slug (current memberships only)
        if "faction" in params:
            faction_slug = (params.get("faction") or "").strip()
            if (
                not faction_slug
                or not Faction.objects.filter(
                    slug=faction_slug, status__in=PUBLIC_FACTION_STATUSES
                ).exists()
            ):
                raise ValidationError(
                    {
                        "faction": [
                            f"Invalid faction '{faction_slug}'. "
                            "Faction does not exist or is not public."
                        ]
                    }
                )
            queryset = queryset.filter(
                memberships__faction__slug=faction_slug,
                memberships__ended_on__isnull=True,
            )

        # 4. Filter by featured status
        if "featured" in params:
            featured_val = (params.get("featured") or "").strip().lower()
            if featured_val in ("true", "1"):
                queryset = queryset.filter(is_featured=True)
            elif featured_val in ("false", "0"):
                queryset = queryset.filter(is_featured=False)
            else:
                raise ValidationError(
                    {"featured": ["Must be a valid boolean ('true', 'false', '1', or '0')."]}
                )

        return queryset.distinct()


class PersonDetailView(generics.RetrieveAPIView):
    """Public read-only detail view of a single person profile, looked up by slug.

    Only published records are accessible. Draft or hidden records return HTTP 404.
    Includes active categories, current faction memberships, and public platform accounts.
    """

    serializer_class = PersonDetailSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]
    lookup_field = "slug"

    def get_queryset(self):
        return Person.objects.filter(status=PersonStatus.PUBLISHED).prefetch_related(
            Prefetch("categories", queryset=Category.objects.filter(is_active=True)),
            Prefetch(
                "memberships",
                queryset=Membership.objects.filter(
                    ended_on__isnull=True,
                    faction__status__in=PUBLIC_FACTION_STATUSES,
                ).select_related("faction"),
            ),
            Prefetch(
                "platform_accounts",
                queryset=PlatformAccount.objects.filter(platform__is_active=True).select_related(
                    "platform"
                ),
            ),
        )


class FactionListView(generics.ListAPIView):
    """Public read-only list of organizations and gangs.

    Only factions with recognized public statuses ('active', 'inactive', 'disbanded')
    are returned.
    Supports:
    - Search by name and tag: `?search=<term>`
    - Filter by status: `?status=<status>` (public statuses only)

    Invalid query parameter values return HTTP 400 Bad Request.
    Write methods return HTTP 405 Method Not Allowed.
    """

    serializer_class = FactionListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        params = self.request.query_params
        allowed = {"search", "status", "page", "page_size", "format"}
        unrecognized = set(params.keys()) - allowed
        if unrecognized:
            raise ValidationError(
                {"detail": f"Unrecognized query parameter(s): {', '.join(sorted(unrecognized))}."}
            )

        queryset = Faction.objects.filter(status__in=PUBLIC_FACTION_STATUSES).annotate(
            member_count=Count(
                "memberships",
                filter=Q(
                    memberships__ended_on__isnull=True,
                    memberships__person__status=PersonStatus.PUBLISHED,
                ),
                distinct=True,
            )
        )

        # 1. Search by name and tag
        search = params.get("search")
        if search:
            search = search.strip()
            if search:
                queryset = queryset.filter(Q(name__icontains=search) | Q(tag__icontains=search))

        # 2. Filter by status (public statuses only)
        if "status" in params:
            status_val = (params.get("status") or "").strip().lower()
            if status_val not in PUBLIC_FACTION_STATUSES:
                valid_choices = ", ".join(PUBLIC_FACTION_STATUSES)
                raise ValidationError(
                    {
                        "status": [
                            f"Invalid status '{status_val}'. "
                            f"Valid public statuses: {valid_choices}."
                        ]
                    }
                )
            queryset = queryset.filter(status=status_val)

        return queryset.order_by("name")


class FactionDetailView(generics.RetrieveAPIView):
    """Public read-only detail view of a single faction, looked up by slug.

    Only public factions are accessible.
    Detail includes current members (ended_on is None) with published profiles,
    their role, and their platform account links. Former members are never shown.
    """

    serializer_class = FactionDetailSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "head", "options"]
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Faction.objects.filter(status__in=PUBLIC_FACTION_STATUSES)
            .annotate(
                member_count=Count(
                    "memberships",
                    filter=Q(
                        memberships__ended_on__isnull=True,
                        memberships__person__status=PersonStatus.PUBLISHED,
                    ),
                    distinct=True,
                )
            )
            .prefetch_related(
                Prefetch(
                    "memberships",
                    queryset=Membership.objects.filter(
                        ended_on__isnull=True,
                        person__status=PersonStatus.PUBLISHED,
                    )
                    .select_related("person")
                    .prefetch_related(
                        Prefetch(
                            "person__platform_accounts",
                            queryset=PlatformAccount.objects.filter(
                                platform__is_active=True
                            ).select_related("platform"),
                        )
                    ),
                )
            )
        )


class CategoryListView(generics.ListAPIView):
    """Public read-only list of active categories."""

    serializer_class = CategorySerializer
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
        return Category.objects.filter(is_active=True)
