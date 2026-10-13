"""Serializers for the Platforms app."""

from rest_framework import serializers

from apps.platforms.models import Platform, PlatformAccount, PlatformLiveStatus


class PlatformSerializer(serializers.ModelSerializer):
    """Public read-only serializer for external platforms.

    Explicitly includes slug and livestream support flag.
    No credentials or internal secrets are exposed.
    """

    class Meta:
        model = Platform
        fields = [
            "id",
            "name",
            "slug",
            "kind",
            "supports_live",
            "url_template",
            "sort_order",
        ]
        read_only_fields = fields


class PlatformAccountSerializer(serializers.ModelSerializer):
    """Public read-only serializer for a creator's platform account link.

    Maintained as a standalone serializer so live streaming metadata
    (e.g. stream status, viewer count) can be added in future phases
    without breaking or changing the API contract shape.
    Staff notes and internal credentials are strictly excluded.
    """

    platform = PlatformSerializer(read_only=True)

    class Meta:
        model = PlatformAccount
        fields = [
            "id",
            "platform",
            "handle",
            "external_id",
            "url",
            "is_verified",
        ]
        read_only_fields = fields


class PlatformLiveStatusSerializer(serializers.ModelSerializer):
    handle = serializers.CharField(
        source="platform_account.handle",
        read_only=True,
    )
    platform = serializers.CharField(
        source="platform_account.platform.slug",
        read_only=True,
    )
    person_slug = serializers.CharField(
        source="platform_account.person.slug",
        read_only=True,
    )
    display_name = serializers.CharField(
        source="platform_account.person.display_name",
        read_only=True,
    )
    is_live = serializers.SerializerMethodField()
    viewer_count = serializers.SerializerMethodField()
    is_stale = serializers.SerializerMethodField()

    class Meta:
        model = PlatformLiveStatus
        fields = [
            "handle",
            "platform",
            "person_slug",
            "display_name",
            "is_live",
            "is_stale",
            "stream_title",
            "viewer_count",
            "stream_started_at",
            "last_seen_live_at",
            "last_stream_ended_at",
            "last_checked_at",
        ]

    def get_is_live(self, obj) -> bool:
        if hasattr(obj, "effective_is_live"):
            return bool(obj.effective_is_live)
        return obj.is_currently_live()

    def get_viewer_count(self, obj) -> int:
        if hasattr(obj, "effective_viewer_count"):
            return obj.effective_viewer_count
        return obj.viewer_count if obj.is_currently_live() else 0

    def get_is_stale(self, obj) -> bool:
        return obj.is_stale

