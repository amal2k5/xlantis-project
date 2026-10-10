"""Tests for the Platforms REST API endpoints."""

import pytest
from rest_framework.test import APIClient

from apps.platforms.models import Platform, PlatformKind


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
