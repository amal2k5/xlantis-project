"""Serializers for the Directory app.

Includes serializers for Category, Person, Faction, and Membership models.
All serializers use explicit fields with no cyclic recursion and no internal/secret fields.
"""

from rest_framework import serializers

from apps.directory.models import (
    Category,
    Faction,
    FactionStatus,
    Membership,
    Person,
    PersonStatus,
)
from apps.platforms.serializers import PlatformAccountSerializer

# Exact public faction statuses: all officially recognized server statuses
PUBLIC_FACTION_STATUSES = [
    FactionStatus.ACTIVE.value,
    FactionStatus.INACTIVE.value,
    FactionStatus.DISBANDED.value,
]


class CategorySerializer(serializers.ModelSerializer):
    """Public read-only serializer for category classifications."""

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "sort_order",
        ]
        read_only_fields = fields


class FactionSummarySerializer(serializers.ModelSerializer):
    """Compact Faction representation embedded in person membership lists."""

    class Meta:
        model = Faction
        fields = [
            "id",
            "name",
            "slug",
            "tag",
            "description",
            "logo_url",
            "status",
        ]
        read_only_fields = fields


class PersonSummarySerializer(serializers.ModelSerializer):
    """Compact Person profile representation embedded in faction member rosters."""

    class Meta:
        model = Person
        fields = [
            "id",
            "display_name",
            "slug",
            "avatar_url",
            "is_featured",
        ]
        read_only_fields = fields


class PersonMembershipSerializer(serializers.ModelSerializer):
    """Serializer representing a person's affiliation with a faction.

    Only current memberships (ended_on is None) in public factions are shown.
    """

    faction = FactionSummarySerializer(read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "role",
            "started_on",
            "ended_on",
            "faction",
        ]
        read_only_fields = fields


class FactionMemberSerializer(serializers.ModelSerializer):
    """Serializer representing a current member on a faction roster.

    Includes the member profile and their verified/public streaming platform accounts.
    """

    person = PersonSummarySerializer(read_only=True)
    platform_accounts = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            "id",
            "role",
            "started_on",
            "ended_on",
            "person",
            "platform_accounts",
        ]
        read_only_fields = fields

    def get_platform_accounts(self, obj):
        """Return platform accounts for the member from active platforms only."""
        active_accounts = [
            acc for acc in obj.person.platform_accounts.all() if acc.platform.is_active
        ]
        return PlatformAccountSerializer(active_accounts, many=True, context=self.context).data


class MembershipSerializer(serializers.ModelSerializer):
    """Standalone public read-only serializer for the Membership model."""

    person_name = serializers.CharField(source="person.display_name", read_only=True)
    person_slug = serializers.CharField(source="person.slug", read_only=True)
    faction_name = serializers.CharField(source="faction.name", read_only=True)
    faction_slug = serializers.CharField(source="faction.slug", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "person_name",
            "person_slug",
            "faction_name",
            "faction_slug",
            "role",
            "started_on",
            "ended_on",
        ]
        read_only_fields = fields


class PersonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for directory person list views.

    Omits heavy nested relationships (detailed memberships, platform accounts)
    to keep page payloads small and query counts optimal.
    """

    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Person
        fields = [
            "id",
            "display_name",
            "slug",
            "bio",
            "avatar_url",
            "is_featured",
            "categories",
        ]
        read_only_fields = fields


class PersonDetailSerializer(serializers.ModelSerializer):
    """Richer serializer for directory person profile detail views.

    Includes categories, current faction memberships (ended_on is None),
    and verified streaming platform accounts.
    """

    categories = CategorySerializer(many=True, read_only=True)
    memberships = serializers.SerializerMethodField()
    platform_accounts = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            "id",
            "display_name",
            "slug",
            "bio",
            "avatar_url",
            "status",
            "is_featured",
            "categories",
            "memberships",
            "platform_accounts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_memberships(self, obj):
        """Return only CURRENT memberships (ended_on is None) in public factions."""
        active_memberships = [
            m
            for m in obj.memberships.all()
            if m.ended_on is None and m.faction.status in PUBLIC_FACTION_STATUSES
        ]
        return PersonMembershipSerializer(active_memberships, many=True, context=self.context).data

    def get_platform_accounts(self, obj):
        """Return platform accounts on active platforms only."""
        active_accounts = [acc for acc in obj.platform_accounts.all() if acc.platform.is_active]
        return PlatformAccountSerializer(active_accounts, many=True, context=self.context).data


class FactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for factions list view.

    Includes summary attributes and current member count without embedding member rosters.
    """

    member_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Faction
        fields = [
            "id",
            "name",
            "slug",
            "tag",
            "description",
            "logo_url",
            "status",
            "member_count",
        ]
        read_only_fields = fields


class FactionDetailSerializer(serializers.ModelSerializer):
    """Richer serializer for faction detail views.

    Includes current active members with their role and external platform account links.
    Former members (ended_on is not None) and draft/hidden persons are strictly excluded.
    """

    member_count = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    memberships = serializers.SerializerMethodField()

    class Meta:
        model = Faction
        fields = [
            "id",
            "name",
            "slug",
            "tag",
            "description",
            "logo_url",
            "status",
            "member_count",
            "members",
            "memberships",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_members(self, obj):
        """Return current members (ended_on is None) with published profiles only."""
        active_memberships = [
            m
            for m in obj.memberships.all()
            if m.ended_on is None and m.person.status == PersonStatus.PUBLISHED
        ]
        return FactionMemberSerializer(active_memberships, many=True, context=self.context).data

    def get_memberships(self, obj):
        """Alias for members to provide backwards compatibility with varied client schemas."""
        return self.get_members(obj)

    def get_member_count(self, obj):
        """Return the count of active published members."""
        if hasattr(obj, "member_count"):
            return obj.member_count
        return len(self.get_members(obj))
