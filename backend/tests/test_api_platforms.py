from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.directory.models import Person, PersonStatus
from apps.platforms.models import (
    Platform,
    PlatformAccount,
    PlatformKind,
    PlatformLiveStatus,
)
from apps.platforms.services.live_tracker import get_live_status, is_account_live


@pytest.mark.django_db
class TestPlatformListAPI:
    """Test suite for GET /api/v1/platforms/."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def setup_platforms(self):
        p1 = Platform.objects.create(
            name="Kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            url_template="https://kick.com/{handle}",
            is_active=True,
            sort_order=1,
        )
        p2 = Platform.objects.create(
            name="YouTube",
            kind=PlatformKind.VIDEO,
            supports_live=True,
            url_template="https://youtube.com/@{handle}",
            is_active=True,
            sort_order=2,
        )
        p3 = Platform.objects.create(
            name="X",
            kind=PlatformKind.SOCIAL,
            supports_live=False,
            url_template="https://x.com/{handle}",
            is_active=True,
            sort_order=3,
        )
        p_inactive = Platform.objects.create(
            name="Deprecated Platform",
            kind=PlatformKind.OTHER,
            supports_live=False,
            is_active=False,
            sort_order=99,
        )
        return {"kick": p1, "yt": p2, "x": p3, "inactive": p_inactive}

    def test_list_active_platforms_only(self, client, setup_platforms):
        """Active platforms are returned; inactive platforms are excluded."""
        response = client.get("/api/v1/platforms/")
        assert response.status_code == 200
        data = response.json()
        results = data["results"] if "results" in data else data

        names = [p["name"] for p in results]
        assert "Kick" in names
        assert "YouTube" in names
        assert "X" in names
        assert "Deprecated Platform" not in names

    def test_livestream_support_flag_included(self, client, setup_platforms):
        """Verify supports_live flag is present and accurate on all platforms."""
        response = client.get("/api/v1/platforms/")
        assert response.status_code == 200
        data = response.json()
        results = data["results"] if "results" in data else data

        platform_map = {p["name"]: p for p in results}
        assert platform_map["Kick"]["supports_live"] is True
        assert platform_map["YouTube"]["supports_live"] is True
        assert platform_map["X"]["supports_live"] is False

    def test_explicit_fields_and_no_secrets(self, client, setup_platforms):
        """Serializer contract has explicit fields, includes slug, and exposes no secrets."""
        response = client.get("/api/v1/platforms/")
        assert response.status_code == 200
        data = response.json()
        results = data["results"] if "results" in data else data

        for item in results:
            assert "id" in item
            assert "name" in item
            assert "slug" in item
            assert "kind" in item
            assert "supports_live" in item
            assert "url_template" in item
            assert "sort_order" in item
            # Verify no secret or internal fields
            assert "secret" not in item
            assert "password" not in item
            assert "token" not in item

    def test_unrecognized_query_param_returns_400(self, client, setup_platforms):
        """Invalid or unexpected query parameters return 400 Bad Request."""
        response = client.get("/api/v1/platforms/?invalid_param=123")
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_write_methods_rejected(self, client, setup_platforms):
        """Public API is read-only; write methods return 405 Method Not Allowed."""
        url = "/api/v1/platforms/"
        assert client.post(url, {"name": "Twitch"}).status_code == 405
        assert client.put(url, {"name": "Twitch"}).status_code == 405
        assert client.patch(url, {"name": "Twitch"}).status_code == 405
        assert client.delete(url).status_code == 405

    def test_query_count_constant(self, client, django_assert_num_queries):
        """Verify query count is constant (1 query for count + 1 for items)."""
        Platform.objects.all().delete()
        for i in range(15):
            Platform.objects.create(name=f"Plat-{i}", is_active=True, sort_order=i)

        # 1 query for count, 1 query for data
        with django_assert_num_queries(2):
            response = client.get("/api/v1/platforms/")
            assert response.status_code == 200


@pytest.mark.django_db
class TestLiveStatusStaleness:
    """Unit tests for PlatformLiveStatus model methods, properties, and helper functions."""

    @pytest.fixture
    def setup_data(self):
        person = Person.objects.create(
            display_name="Test Streamer",
            slug="test-streamer",
            status=PersonStatus.PUBLISHED,
        )
        platform = Platform.objects.create(
            name="Kick",
            slug="kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            is_active=True,
        )
        account = PlatformAccount.objects.create(
            person=person,
            platform=platform,
            handle="streamer_kick",
            url="https://kick.com/streamer_kick",
        )
        return {"person": person, "platform": platform, "account": account}

    def test_recently_checked_live_creator(self, setup_data):
        """A creator checked within the 300s threshold is verified as currently live."""
        account = setup_data["account"]
        now = timezone.now()
        status = PlatformLiveStatus.objects.create(
            platform_account=account,
            is_live=True,
            viewer_count=250,
            stream_title="Live Patrol",
            last_checked_at=now - timedelta(seconds=30),
        )

        assert status.is_currently_live() is True
        assert status.is_stale is False
        assert is_account_live(account) is True
        assert str(status) == f"{account} - LIVE"

    def test_stale_live_record_detected_as_offline(self, setup_data):
        """A record marked is_live=True but checked > 300s ago is recognized as stale/offline."""
        account = setup_data["account"]
        now = timezone.now()
        status = PlatformLiveStatus.objects.create(
            platform_account=account,
            is_live=True,
            viewer_count=500,
            stream_title="Outdated Stream",
            last_checked_at=now - timedelta(minutes=10),
        )

        assert status.is_currently_live() is False
        assert status.is_stale is True
        assert is_account_live(account) is False
        assert str(status) == f"{account} - OFFLINE"

    def test_recently_checked_offline_creator(self, setup_data):
        """A creator marked is_live=False recently is recognized as offline and not stale."""
        account = setup_data["account"]
        now = timezone.now()
        status = PlatformLiveStatus.objects.create(
            platform_account=account,
            is_live=False,
            viewer_count=0,
            last_checked_at=now - timedelta(seconds=45),
        )

        assert status.is_currently_live() is False
        assert status.is_stale is False
        assert is_account_live(account) is False
        assert str(status) == f"{account} - OFFLINE"

    def test_creator_without_live_status_record(self, setup_data):
        """A creator/account with no PlatformLiveStatus defaults cleanly to offline."""
        account = setup_data["account"]
        assert get_live_status(account) is None
        assert is_account_live(account) is False

    def test_boundary_conditions_around_stale_threshold(self, setup_data):
        """Test boundary conditions exactly at, 1s before, and 1s past the 300s threshold."""
        account = setup_data["account"]
        now = timezone.now()
        status = PlatformLiveStatus.objects.create(
            platform_account=account,
            is_live=True,
            viewer_count=100,
            last_checked_at=now,
        )

        # 1. Exactly at boundary (300s): still fresh (cutoff <= last_checked_at)
        status.last_checked_at = now - timedelta(seconds=300)
        assert status.is_currently_live(threshold_seconds=300, now=now) is True
        assert status.check_stale(threshold_seconds=300, now=now) is False

        # 2. 1 second before boundary (299s): fresh
        status.last_checked_at = now - timedelta(seconds=299)
        assert status.is_currently_live(threshold_seconds=300, now=now) is True
        assert status.check_stale(threshold_seconds=300, now=now) is False

        # 3. 1 second past boundary (301s): stale
        status.last_checked_at = now - timedelta(seconds=301)
        assert status.is_currently_live(threshold_seconds=300, now=now) is False
        assert status.check_stale(threshold_seconds=300, now=now) is True

        # 4. last_checked_at is None: stale
        status.last_checked_at = None
        assert status.is_currently_live(threshold_seconds=300, now=now) is False
        assert status.check_stale(threshold_seconds=300, now=now) is True


@pytest.mark.django_db
class TestPlatformLiveStatusAPI:
    """Integration tests for GET /api/v1/platforms/live-status/ endpoint."""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def setup_data(self):
        platform = Platform.objects.create(
            name="Kick",
            slug="kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            is_active=True,
        )
        p1 = Person.objects.create(
            display_name="Fresh Streamer",
            slug="fresh-streamer",
            status=PersonStatus.PUBLISHED,
        )
        p2 = Person.objects.create(
            display_name="Stale Streamer",
            slug="stale-streamer",
            status=PersonStatus.PUBLISHED,
        )
        p3 = Person.objects.create(
            display_name="Offline Streamer",
            slug="offline-streamer",
            status=PersonStatus.PUBLISHED,
        )

        a1 = PlatformAccount.objects.create(person=p1, platform=platform, handle="fresh_k")
        a2 = PlatformAccount.objects.create(person=p2, platform=platform, handle="stale_k")
        a3 = PlatformAccount.objects.create(person=p3, platform=platform, handle="offline_k")

        now = timezone.now()
        s1 = PlatformLiveStatus.objects.create(
            platform_account=a1,
            is_live=True,
            stream_title="Active Right Now",
            viewer_count=1200,
            last_checked_at=now - timedelta(seconds=30),
        )
        s2 = PlatformLiveStatus.objects.create(
            platform_account=a2,
            is_live=True,
            stream_title="Abandoned Stream",
            viewer_count=850,
            last_checked_at=now - timedelta(minutes=15),
        )
        s3 = PlatformLiveStatus.objects.create(
            platform_account=a3,
            is_live=False,
            stream_title="Offline Title",
            viewer_count=0,
            last_checked_at=now - timedelta(seconds=20),
        )
        return {"platform": platform, "s1": s1, "s2": s2, "s3": s3}

    def test_api_returns_legitimate_live_and_stale_records(self, client, setup_data):
        """API sets is_live=False and viewer_count=0 for stale records while preserving fields."""
        response = client.get("/api/v1/platforms/live-status/")
        assert response.status_code == 200
        data = response.json()
        results = data["results"] if "results" in data else data

        res_map = {item["handle"]: item for item in results}

        # 1. Fresh streamer remains LIVE
        fresh = res_map["fresh_k"]
        assert fresh["is_live"] is True
        assert fresh["is_stale"] is False
        assert fresh["viewer_count"] == 1200
        assert fresh["stream_title"] == "Active Right Now"

        # 2. Stale streamer appears OFFLINE with 0 viewers
        stale = res_map["stale_k"]
        assert stale["is_live"] is False
        assert stale["is_stale"] is True
        assert stale["viewer_count"] == 0
        assert stale["stream_title"] == "Abandoned Stream"
        assert stale["last_checked_at"] is not None

        # 3. Offline streamer is OFFLINE
        offline = res_map["offline_k"]
        assert offline["is_live"] is False
        assert offline["is_stale"] is False
        assert offline["viewer_count"] == 0

    def test_api_ordering_places_fresh_live_first(self, client, setup_data):
        """Fresh live streamers are ordered ahead of stale and offline streamers."""
        response = client.get("/api/v1/platforms/live-status/")
        assert response.status_code == 200
        results = response.json()["results"]

        # The fresh live streamer must be first in the list
        assert results[0]["handle"] == "fresh_k"
        assert results[0]["is_live"] is True

        # The remaining streamers must have is_live=False
        for remaining in results[1:]:
            assert remaining["is_live"] is False

    @override_settings(LIVE_STATUS_STALE_THRESHOLD_SECONDS=60)
    def test_override_stale_threshold_setting(self, client, setup_data):
        """Verify dynamic configuration via LIVE_STATUS_STALE_THRESHOLD_SECONDS."""
        # s1 was checked 30 seconds ago (fresh for threshold=60)
        # We simulate s1 checked 75 seconds ago (stale for threshold=60)
        now = timezone.now()
        setup_data["s1"].last_checked_at = now - timedelta(seconds=75)
        setup_data["s1"].save()

        response = client.get("/api/v1/platforms/live-status/")
        assert response.status_code == 200
        results = response.json()["results"]
        res_map = {item["handle"]: item for item in results}

        # With 60s threshold, 75s is now stale
        assert res_map["fresh_k"]["is_live"] is False
        assert res_map["fresh_k"]["is_stale"] is True

