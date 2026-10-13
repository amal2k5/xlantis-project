"""Tests for the Directory REST API endpoints."""

from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.directory.models import (
    Category,
    Faction,
    FactionStatus,
    Membership,
    MembershipRole,
    Person,
    PersonStatus,
)
from apps.platforms.models import Platform, PlatformAccount, PlatformKind


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestPersonAPI:
    """Test suite for Person list and detail endpoints."""

    @pytest.fixture
    def setup_data(self):
        cat_gang = Category.objects.create(name="Gang Member", is_active=True)
        cat_streamer = Category.objects.create(name="Streamer", is_active=True)
        cat_inactive = Category.objects.create(name="Archived Role", is_active=False)

        # Published persons
        p1 = Person.objects.create(
            display_name="Tony Corleone",
            bio="Crime boss of Cleanbois.",
            status=PersonStatus.PUBLISHED,
            is_featured=True,
        )
        p1.categories.add(cat_gang, cat_streamer)

        p2 = Person.objects.create(
            display_name="Buddha",
            bio="Second in command.",
            status=PersonStatus.PUBLISHED,
            is_featured=False,
        )
        p2.categories.add(cat_gang)

        # Draft and Hidden persons (must be strictly hidden from public API)
        p_draft = Person.objects.create(
            display_name="Secret Undercover",
            bio="Draft profile in review.",
            status=PersonStatus.DRAFT,
            is_featured=False,
        )
        p_draft.categories.add(cat_gang)

        p_hidden = Person.objects.create(
            display_name="Suspended User",
            bio="Temporarily hidden profile.",
            status=PersonStatus.HIDDEN,
            is_featured=False,
        )

        # Platforms and Accounts
        plat_kick = Platform.objects.create(
            name="Kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            is_active=True,
        )
        plat_inactive = Platform.objects.create(
            name="Mixer",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            is_active=False,
        )

        acc1 = PlatformAccount.objects.create(
            person=p1,
            platform=plat_kick,
            handle="tony_kick",
            url="https://kick.com/tony_kick",
            is_verified=True,
            notes="Private staff moderation notes - secret",
        )
        # Inactive platform account
        PlatformAccount.objects.create(
            person=p1,
            platform=plat_inactive,
            handle="tony_mixer",
            url="https://mixer.com/tony_mixer",
        )

        # Factions and Memberships
        f_active = Faction.objects.create(
            name="Cleanbois",
            tag="CB",
            status=FactionStatus.ACTIVE,
        )
        f_former = Faction.objects.create(
            name="Leanbois",
            tag="LB",
            status=FactionStatus.DISBANDED,
        )

        # Current membership for p1 in Cleanbois
        m_curr = Membership.objects.create(
            person=p1,
            faction=f_active,
            role=MembershipRole.LEADER,
            started_on=date(2026, 1, 1),
            ended_on=None,
        )
        # Former membership for p1 in Leanbois
        m_former = Membership.objects.create(
            person=p1,
            faction=f_former,
            role=MembershipRole.MEMBER,
            started_on=date(2024, 1, 1),
            ended_on=date(2025, 1, 1),
        )

        return {
            "p1": p1,
            "p2": p2,
            "p_draft": p_draft,
            "p_hidden": p_hidden,
            "cat_gang": cat_gang,
            "cat_streamer": cat_streamer,
            "cat_inactive": cat_inactive,
            "plat_kick": plat_kick,
            "acc1": acc1,
            "f_active": f_active,
            "f_former": f_former,
            "m_curr": m_curr,
            "m_former": m_former,
        }

    # 1. List Endpoint Tests
    def test_person_list_returns_published_only(self, api_client, setup_data):
        """Only published persons are returned; draft and hidden are excluded."""
        response = api_client.get("/api/v1/directory/persons/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

        slugs = [item["slug"] for item in data["results"]]
        assert "tony-corleone" in slugs
        assert "buddha" in slugs
        assert setup_data["p_draft"].slug not in slugs
        assert setup_data["p_hidden"].slug not in slugs

    def test_person_list_serializer_is_light(self, api_client, setup_data):
        """List serializer uses lightweight fields; excludes memberships and platform accounts."""
        response = api_client.get("/api/v1/directory/persons/")
        assert response.status_code == 200
        first_item = response.json()["results"][0]

        # Light fields present
        assert "id" in first_item
        assert "display_name" in first_item
        assert "slug" in first_item
        assert "avatar_url" in first_item
        assert "is_featured" in first_item
        assert "categories" in first_item

        # Heavy relations omitted in list view
        assert "memberships" not in first_item
        assert "platform_accounts" not in first_item

    def test_person_search_by_display_name_and_bio(self, api_client, setup_data):
        """Search query matches display_name or bio (case-insensitive)."""
        # Search by display name
        res1 = api_client.get("/api/v1/directory/persons/?search=Tony")
        assert res1.status_code == 200
        assert res1.json()["count"] == 1
        assert res1.json()["results"][0]["slug"] == "tony-corleone"

        # Search by bio
        res2 = api_client.get("/api/v1/directory/persons/?search=command")
        assert res2.status_code == 200
        assert res2.json()["count"] == 1
        assert res2.json()["results"][0]["slug"] == "buddha"

    def test_person_search_empty_results(self, api_client, setup_data):
        """Search matching nothing returns 200 OK with empty results list."""
        res = api_client.get("/api/v1/directory/persons/?search=NonExistentCharacterXYZ")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_person_filter_by_category(self, api_client, setup_data):
        """Filter by valid active category slug."""
        res = api_client.get("/api/v1/directory/persons/?category=streamer")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 1
        assert data["results"][0]["slug"] == "tony-corleone"

    def test_person_filter_by_invalid_category_returns_400(self, api_client, setup_data):
        """Filtering by non-existent or inactive category returns 400."""
        # Non-existent category
        res1 = api_client.get("/api/v1/directory/persons/?category=nonexistent-slug")
        assert res1.status_code == 400
        assert "category" in res1.json()

        # Inactive category
        res2 = api_client.get("/api/v1/directory/persons/?category=archived-role")
        assert res2.status_code == 400
        assert "category" in res2.json()

    def test_person_filter_by_featured(self, api_client, setup_data):
        """Filter by boolean featured status (supports 'true', 'false', '1', '0')."""
        res_true = api_client.get("/api/v1/directory/persons/?featured=true")
        assert res_true.status_code == 200
        assert res_true.json()["count"] == 1
        assert res_true.json()["results"][0]["slug"] == "tony-corleone"

        res_false = api_client.get("/api/v1/directory/persons/?featured=false")
        assert res_false.status_code == 200
        assert res_false.json()["count"] == 1
        assert res_false.json()["results"][0]["slug"] == "buddha"

        res_one = api_client.get("/api/v1/directory/persons/?featured=1")
        assert res_one.status_code == 200
        assert res_one.json()["count"] == 1

        res_zero = api_client.get("/api/v1/directory/persons/?featured=0")
        assert res_zero.status_code == 200
        assert res_zero.json()["count"] == 1

    def test_person_filter_by_invalid_featured_returns_400(self, api_client, setup_data):
        """Invalid boolean value returns 400 Bad Request."""
        res = api_client.get("/api/v1/directory/persons/?featured=maybe")
        assert res.status_code == 400
        assert "featured" in res.json()

    def test_person_filter_by_faction(self, api_client, setup_data):
        """Filter by valid active faction slug matches current memberships only."""
        res_current = api_client.get("/api/v1/directory/persons/?faction=cleanbois")
        assert res_current.status_code == 200
        data = res_current.json()
        assert data["count"] == 1
        assert data["results"][0]["slug"] == "tony-corleone"

        # Former/ended membership in leanbois must NOT match
        res_ended = api_client.get("/api/v1/directory/persons/?faction=leanbois")
        assert res_ended.status_code == 200
        assert res_ended.json()["count"] == 0

    def test_person_filter_by_invalid_faction_returns_400(self, api_client, setup_data):
        """Filtering by non-existent or inactive faction returns 400."""
        res = api_client.get("/api/v1/directory/persons/?faction=nonexistent-gang")
        assert res.status_code == 400
        assert "faction" in res.json()

    def test_person_filter_combined_search_category_faction(self, api_client, setup_data):
        """Combined filters narrow down results accurately."""
        res = api_client.get(
            "/api/v1/directory/persons/?search=Tony&category=gang-member&faction=cleanbois"
        )
        assert res.status_code == 200
        assert res.json()["count"] == 1
        assert res.json()["results"][0]["slug"] == "tony-corleone"

    def test_person_page_size_parameter(self, api_client):
        """Custom ?page_size parameter overrides default pagination size up to max."""
        Person.objects.all().delete()
        for i in range(25):
            Person.objects.create(
                display_name=f"Player {i:02d}",
                status=PersonStatus.PUBLISHED,
            )

        res = api_client.get("/api/v1/directory/persons/?page_size=10")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 25
        assert len(data["results"]) == 10

    def test_person_unrecognized_query_param_returns_400(self, api_client, setup_data):
        """Unrecognized query parameters return 400 Bad Request."""
        res = api_client.get("/api/v1/directory/persons/?bad_param=123")
        assert res.status_code == 400
        assert "detail" in res.json()

    def test_person_pagination(self, api_client):
        """Verify pagination with 25 records produces 20 on page 1 and 5 on page 2."""
        Person.objects.all().delete()
        for i in range(25):
            Person.objects.create(
                display_name=f"Player {i:02d}",
                status=PersonStatus.PUBLISHED,
            )

        # Page 1
        res1 = api_client.get("/api/v1/directory/persons/")
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["count"] == 25
        assert len(d1["results"]) == 20
        assert d1["next"] is not None
        assert d1["previous"] is None

        # Page 2
        res2 = api_client.get("/api/v1/directory/persons/?page=2")
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2["count"] == 25
        assert len(d2["results"]) == 5
        assert d2["next"] is None
        assert d2["previous"] is not None

    def test_person_list_query_count_constant(self, api_client, django_assert_num_queries):
        """Verify constant query count regardless of item count (O(1) database queries)."""
        Person.objects.all().delete()
        for i in range(15):
            Person.objects.create(
                display_name=f"Player {i}",
                status=PersonStatus.PUBLISHED,
            )

        # 1 query for count, 1 for person slice, 1 for categories prefetch = 3 queries
        with django_assert_num_queries(3):
            res = api_client.get("/api/v1/directory/persons/")
            assert res.status_code == 200

    def test_person_people_alias_endpoint(self, api_client, setup_data):
        """Frontend alias /api/v1/directory/people/ operates identically."""
        res = api_client.get("/api/v1/directory/people/")
        assert res.status_code == 200
        assert res.json()["count"] == 2

    # 2. Detail Endpoint Tests
    def test_person_detail_slug_lookup_and_rich_serializer(self, api_client, setup_data):
        """Detail endpoint returns rich serializer with categories, memberships, accounts."""
        res = api_client.get("/api/v1/directory/persons/tony-corleone/")
        assert res.status_code == 200
        data = res.json()

        assert data["display_name"] == "Tony Corleone"
        assert data["slug"] == "tony-corleone"
        assert data["status"] == "published"
        assert "categories" in data
        assert "memberships" in data
        assert "platform_accounts" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_person_detail_current_vs_former_memberships(self, api_client, setup_data):
        """Only CURRENT memberships (ended_on is None) are included in person detail."""
        res = api_client.get("/api/v1/directory/persons/tony-corleone/")
        assert res.status_code == 200
        memberships = res.json()["memberships"]

        assert len(memberships) == 1
        assert memberships[0]["faction"]["slug"] == "cleanbois"
        assert memberships[0]["role"] == "leader"
        assert memberships[0]["ended_on"] is None

        # Verify former membership in Leanbois is NOT present
        faction_slugs = [m["faction"]["slug"] for m in memberships]
        assert "leanbois" not in faction_slugs

    def test_person_detail_platform_accounts_excludes_inactive_platforms(
        self, api_client, setup_data
    ):
        """Only platform accounts on active platforms are included; notes are excluded."""
        res = api_client.get("/api/v1/directory/persons/tony-corleone/")
        assert res.status_code == 200
        accounts = res.json()["platform_accounts"]

        assert len(accounts) == 1
        account = accounts[0]
        assert account["platform"]["name"] == "Kick"
        assert account["handle"] == "tony_kick"
        assert account["is_verified"] is True
        # Verify internal notes is not exposed
        assert "notes" not in account

    def test_person_detail_draft_and_hidden_return_404(self, api_client, setup_data):
        """Draft or hidden persons return 404 Not Found."""
        res_draft = api_client.get(f"/api/v1/directory/persons/{setup_data['p_draft'].slug}/")
        assert res_draft.status_code == 404

        res_hidden = api_client.get(f"/api/v1/directory/persons/{setup_data['p_hidden'].slug}/")
        assert res_hidden.status_code == 404

    def test_person_detail_nonexistent_slug_returns_404(self, api_client):
        """Non-existent slug returns 404 Not Found."""
        res = api_client.get("/api/v1/directory/persons/totally-nonexistent-slug/")
        assert res.status_code == 404

    def test_person_write_rejection(self, api_client, setup_data):
        """Write methods on person list and detail return 405 Method Not Allowed."""
        list_url = "/api/v1/directory/persons/"
        detail_url = "/api/v1/directory/persons/tony-corleone/"

        for url in (list_url, detail_url):
            assert api_client.post(url, {"display_name": "Test"}).status_code == 405
            assert api_client.put(url, {"display_name": "Test"}).status_code == 405
            assert api_client.patch(url, {"display_name": "Test"}).status_code == 405
            assert api_client.delete(url).status_code == 405


@pytest.mark.django_db
class TestFactionAPI:
    """Test suite for Faction list and detail endpoints."""

    @pytest.fixture
    def setup_data(self):
        f1 = Faction.objects.create(
            name="The Syndicate",
            tag="SYN",
            description="Controlling port transit.",
            status=FactionStatus.ACTIVE,
        )
        f2 = Faction.objects.create(
            name="Redline Racers",
            tag="RLR",
            description="Midnight expressway racers.",
            status=FactionStatus.INACTIVE,
        )
        f3 = Faction.objects.create(
            name="Lost MC",
            tag="LMC",
            description="Former motorcycle club.",
            status=FactionStatus.DISBANDED,
        )

        # Published members
        p1 = Person.objects.create(
            display_name="Marcus Vance",
            status=PersonStatus.PUBLISHED,
        )
        p2 = Person.objects.create(
            display_name="Elena Rostova",
            status=PersonStatus.PUBLISHED,
        )

        # Draft person
        p_draft = Person.objects.create(
            display_name="Pending Applicant",
            status=PersonStatus.DRAFT,
        )

        # Platform accounts for p1
        plat_kick = Platform.objects.create(
            name="Kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            is_active=True,
        )
        PlatformAccount.objects.create(
            person=p1,
            platform=plat_kick,
            handle="marcus_live",
            url="https://kick.com/marcus_live",
            is_verified=True,
            notes="Staff internal notes",
        )

        # Memberships for f1 (The Syndicate)
        # Current published member
        Membership.objects.create(
            person=p1,
            faction=f1,
            role=MembershipRole.LEADER,
            started_on=date(2026, 1, 1),
            ended_on=None,
        )
        # Former member (ended_on populated)
        Membership.objects.create(
            person=p2,
            faction=f1,
            role=MembershipRole.MEMBER,
            started_on=date(2025, 1, 1),
            ended_on=date(2025, 6, 1),
        )
        # Current member who is DRAFT (must be excluded from public roster)
        Membership.objects.create(
            person=p_draft,
            faction=f1,
            role=MembershipRole.PROSPECT,
            started_on=date(2026, 2, 1),
            ended_on=None,
        )

        return {
            "f1": f1,
            "f2": f2,
            "f3": f3,
            "p1": p1,
            "p2": p2,
            "p_draft": p_draft,
            "plat_kick": plat_kick,
        }

    # 1. List Endpoint Tests
    def test_faction_list_returns_public_statuses(self, api_client, setup_data):
        """Active, inactive, and disbanded factions are returned in list."""
        res = api_client.get("/api/v1/directory/factions/")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 3

        statuses = {item["status"] for item in data["results"]}
        assert statuses == {"active", "inactive", "disbanded"}

    def test_faction_list_serializer_is_light(self, api_client, setup_data):
        """List serializer includes member_count and omits full member rosters."""
        res = api_client.get("/api/v1/directory/factions/")
        assert res.status_code == 200
        first_item = res.json()["results"][0]

        assert "id" in first_item
        assert "name" in first_item
        assert "slug" in first_item
        assert "tag" in first_item
        assert "member_count" in first_item

        # Detailed member rosters are omitted in list view
        assert "members" not in first_item

    def test_faction_list_member_count_counts_current_published_only(self, api_client, setup_data):
        """member_count on faction list counts only active (ended_on=None) published members."""
        res = api_client.get("/api/v1/directory/factions/?search=Syndicate")
        assert res.status_code == 200
        item = res.json()["results"][0]
        # Only p1 is current and published (p2 is former, p_draft is draft)
        assert item["member_count"] == 1

    def test_faction_search_by_name_and_tag(self, api_client, setup_data):
        """Search matches either faction name or tag."""
        # Search by tag
        res_tag = api_client.get("/api/v1/directory/factions/?search=RLR")
        assert res_tag.status_code == 200
        assert res_tag.json()["count"] == 1
        assert res_tag.json()["results"][0]["slug"] == "redline-racers"

        # Search by name
        res_name = api_client.get("/api/v1/directory/factions/?search=Syndicate")
        assert res_name.status_code == 200
        assert res_name.json()["count"] == 1
        assert res_name.json()["results"][0]["slug"] == "the-syndicate"

    def test_faction_search_empty_results(self, api_client, setup_data):
        """Search matching nothing returns 200 OK with empty results list."""
        res = api_client.get("/api/v1/directory/factions/?search=NonExistentGangXYZ")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_faction_filter_by_status(self, api_client, setup_data):
        """Filter by recognized public status values ('active', 'inactive', 'disbanded')."""
        res_active = api_client.get("/api/v1/directory/factions/?status=active")
        assert res_active.status_code == 200
        assert res_active.json()["count"] == 1
        assert res_active.json()["results"][0]["slug"] == "the-syndicate"

        res_inactive = api_client.get("/api/v1/directory/factions/?status=inactive")
        assert res_inactive.status_code == 200
        assert res_inactive.json()["count"] == 1
        assert res_inactive.json()["results"][0]["slug"] == "redline-racers"

        res_disbanded = api_client.get("/api/v1/directory/factions/?status=disbanded")
        assert res_disbanded.status_code == 200
        assert res_disbanded.json()["count"] == 1
        assert res_disbanded.json()["results"][0]["slug"] == "lost-mc"

    def test_faction_filter_by_invalid_status_returns_400(self, api_client, setup_data):
        """Invalid or non-public status values return 400 Bad Request."""
        res = api_client.get("/api/v1/directory/factions/?status=unknown_status")
        assert res.status_code == 400
        assert "status" in res.json()

    def test_faction_unrecognized_query_param_returns_400(self, api_client, setup_data):
        """Unrecognized query parameters return 400 Bad Request."""
        res = api_client.get("/api/v1/directory/factions/?bad_param=123")
        assert res.status_code == 400
        assert "detail" in res.json()

    def test_faction_pagination(self, api_client):
        """Verify pagination with 25 factions produces 20 on page 1 and 5 on page 2."""
        Faction.objects.all().delete()
        for i in range(25):
            Faction.objects.create(name=f"Faction {i:02d}", status=FactionStatus.ACTIVE)

        res1 = api_client.get("/api/v1/directory/factions/")
        assert res1.status_code == 200
        d1 = res1.json()
        assert d1["count"] == 25
        assert len(d1["results"]) == 20
        assert d1["next"] is not None

        res2 = api_client.get("/api/v1/directory/factions/?page=2")
        assert res2.status_code == 200
        d2 = res2.json()
        assert d2["count"] == 25
        assert len(d2["results"]) == 5
        assert d2["next"] is None

    def test_faction_page_size_parameter(self, api_client):
        """Custom ?page_size parameter overrides default pagination size up to max."""
        Faction.objects.all().delete()
        for i in range(25):
            Faction.objects.create(name=f"Faction {i:02d}", status=FactionStatus.ACTIVE)

        res = api_client.get("/api/v1/directory/factions/?page_size=10")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] == 25
        assert len(data["results"]) == 10

    def test_faction_list_query_count_constant(self, api_client, django_assert_num_queries):
        """Verify constant query count (1 count query + 1 data query with annotation = 2)."""
        Faction.objects.all().delete()
        for i in range(15):
            Faction.objects.create(name=f"Faction {i}", status=FactionStatus.ACTIVE)

        with django_assert_num_queries(2):
            res = api_client.get("/api/v1/directory/factions/")
            assert res.status_code == 200

    # 2. Detail Endpoint Tests
    def test_faction_detail_slug_lookup_and_current_members(self, api_client, setup_data):
        """Detail endpoint returns current published members with role and platform accounts."""
        res = api_client.get("/api/v1/directory/factions/the-syndicate/")
        assert res.status_code == 200
        data = res.json()

        assert data["name"] == "The Syndicate"
        assert data["slug"] == "the-syndicate"
        assert data["member_count"] == 1

        members = data["members"]
        assert len(members) == 1

        member = members[0]
        assert member["role"] == "leader"
        assert member["ended_on"] is None
        assert member["person"]["slug"] == "marcus-vance"

        # Platform accounts for the member
        accounts = member["platform_accounts"]
        assert len(accounts) == 1
        assert accounts[0]["platform"]["name"] == "Kick"
        assert accounts[0]["handle"] == "marcus_live"
        assert "notes" not in accounts[0]

    def test_faction_detail_former_members_never_shown(self, api_client, setup_data):
        """Former members (ended_on populated) are NEVER shown in the faction members roster."""
        res = api_client.get("/api/v1/directory/factions/the-syndicate/")
        assert res.status_code == 200
        data = res.json()

        member_slugs = [m["person"]["slug"] for m in data["members"]]
        assert "elena-rostova" not in member_slugs

    def test_faction_detail_draft_members_never_shown(self, api_client, setup_data):
        """Members with draft profile status are NEVER exposed in the faction roster."""
        res = api_client.get("/api/v1/directory/factions/the-syndicate/")
        assert res.status_code == 200
        data = res.json()

        member_slugs = [m["person"]["slug"] for m in data["members"]]
        assert setup_data["p_draft"].slug not in member_slugs

    def test_faction_detail_nonexistent_slug_returns_404(self, api_client):
        """Non-existent faction slug returns 404 Not Found."""
        res = api_client.get("/api/v1/directory/factions/nonexistent-gang-slug/")
        assert res.status_code == 404

    def test_faction_write_rejection(self, api_client, setup_data):
        """Write methods on faction list and detail return 405 Method Not Allowed."""
        list_url = "/api/v1/directory/factions/"
        detail_url = "/api/v1/directory/factions/the-syndicate/"

        for url in (list_url, detail_url):
            assert api_client.post(url, {"name": "Test"}).status_code == 405
            assert api_client.put(url, {"name": "Test"}).status_code == 405
            assert api_client.patch(url, {"name": "Test"}).status_code == 405
            assert api_client.delete(url).status_code == 405


@pytest.mark.django_db
class TestCategoryAPI:
    """Test suite for Category list endpoint."""

    @pytest.fixture
    def setup_data(self):
        c1 = Category.objects.create(name="Gang Member", is_active=True, sort_order=1)
        c2 = Category.objects.create(name="Law Enforcement", is_active=True, sort_order=2)
        c3 = Category.objects.create(name="Archived Tag", is_active=False, sort_order=3)
        return {"c1": c1, "c2": c2, "c3": c3}

    def test_list_active_categories_only(self, api_client, setup_data):
        """Only active categories are returned; inactive are excluded."""
        res = api_client.get("/api/v1/directory/categories/")
        assert res.status_code == 200
        data = res.json()
        results = data["results"] if "results" in data else data

        slugs = [c["slug"] for c in results]
        assert "gang-member" in slugs
        assert "law-enforcement" in slugs
        assert "archived-tag" not in slugs

    def test_category_unrecognized_query_param_returns_400(self, api_client, setup_data):
        """Unrecognized query parameters return 400 Bad Request."""
        res = api_client.get("/api/v1/directory/categories/?foo=bar")
        assert res.status_code == 400
        assert "detail" in res.json()

    def test_category_write_rejection(self, api_client, setup_data):
        """Write methods return 405 Method Not Allowed."""
        url = "/api/v1/directory/categories/"
        assert api_client.post(url, {"name": "New Cat"}).status_code == 405
        assert api_client.put(url, {"name": "New Cat"}).status_code == 405
        assert api_client.patch(url, {"name": "New Cat"}).status_code == 405
        assert api_client.delete(url).status_code == 405


@pytest.mark.django_db
class TestDirectoryRootAPI:
    """Verify Directory root endpoint remains functional and unchanged."""

    def test_directory_root_endpoint(self, api_client):
        res = api_client.get("/api/v1/directory/")
        assert res.status_code == 200
        data = res.json()
        assert data["module"] == "directory"
        assert data["status"] == "ready"
