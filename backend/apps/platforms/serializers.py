"""Serializers for the Platforms app."""

from rest_framework import serializers

from apps.platforms.models import Platform, PlatformAccount


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
