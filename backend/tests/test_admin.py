"""Unit tests for Directory and Platforms Django Admin configurations."""

from datetime import date

import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory

from apps.directory.admin import (
    CategoryAdmin,
    CurrentMembershipFilter,
    FactionAdmin,
    MembershipAdmin,
    PersonAdmin,
)
from apps.directory.models import Category, Faction, Membership, MembershipRole, Person
from apps.platforms.admin import PlatformAccountAdmin, PlatformAdmin
from apps.platforms.models import Platform, PlatformAccount, PlatformKind


@pytest.mark.django_db
class TestAdminRegistrations:
    """Verify all expected models are registered with correct admin classes."""

    def test_directory_models_registered(self):
        assert Category in site._registry
        assert isinstance(site._registry[Category], CategoryAdmin)

        assert Person in site._registry
        assert isinstance(site._registry[Person], PersonAdmin)

        assert Faction in site._registry
        assert isinstance(site._registry[Faction], FactionAdmin)

        assert Membership in site._registry
        assert isinstance(site._registry[Membership], MembershipAdmin)

    def test_platforms_models_registered(self):
        assert Platform in site._registry
        assert isinstance(site._registry[Platform], PlatformAdmin)

        assert PlatformAccount in site._registry
        assert isinstance(site._registry[PlatformAccount], PlatformAccountAdmin)


@pytest.mark.django_db
class TestDirectoryAdminFunctionality:
    """Verify custom admin methods, annotations, and filters for Directory app."""

    def test_category_admin_person_count(self):
        cat = Category.objects.create(name="Streamer")
        person = Person.objects.create(display_name="Speedy")
        person.categories.add(cat)

        request = RequestFactory().get("/admin/directory/category/")
        admin_instance = CategoryAdmin(Category, site)
        qs = admin_instance.get_queryset(request)
        annotated_cat = qs.get(id=cat.id)

        assert admin_instance.person_count(annotated_cat) == 1

    def test_person_admin_current_gangs_display(self):
        person = Person.objects.create(display_name="Tony Corleone")
        faction = Faction.objects.create(name="Cleanbois", tag="CB")

        admin_instance = PersonAdmin(Person, site)
        request = RequestFactory().get("/admin/directory/person/")

        # Case 1: No memberships
        assert admin_instance.get_current_gangs(person) == "-"

        # Case 2: Active membership
        Membership.objects.create(
            person=person,
            faction=faction,
            role=MembershipRole.LEADER,
            started_on=date(2026, 1, 1),
        )

        qs = admin_instance.get_queryset(request)
        annotated_person = qs.get(id=person.id)
        assert admin_instance.get_current_gangs(annotated_person) == "CB"

    def test_faction_admin_active_member_count(self):
        faction = Faction.objects.create(name="Mandem", tag="MDM")
        p1 = Person.objects.create(display_name="Tommy")
        p2 = Person.objects.create(display_name="Dean")

        # Active membership
        Membership.objects.create(
            person=p1,
            faction=faction,
            role=MembershipRole.LEADER,
            started_on=date(2026, 1, 1),
        )
        # Ended membership
        Membership.objects.create(
            person=p2,
            faction=faction,
            role=MembershipRole.MEMBER,
            started_on=date(2025, 1, 1),
            ended_on=date(2025, 6, 1),
        )

        admin_instance = FactionAdmin(Faction, site)
        request = RequestFactory().get("/admin/directory/faction/")
        qs = admin_instance.get_queryset(request)
        annotated_faction = qs.get(id=faction.id)

        # Only the 1 active member should be counted
        assert admin_instance.current_member_count(annotated_faction) == 1

    def test_membership_admin_is_current_and_filter(self):
        p1 = Person.objects.create(display_name="Lang")
        p2 = Person.objects.create(display_name="Buddha")
        faction = Faction.objects.create(name="Roosters")

        m_active = Membership.objects.create(
            person=p1,
            faction=faction,
            started_on=date(2026, 1, 1),
        )
        m_ended = Membership.objects.create(
            person=p2,
            faction=faction,
            started_on=date(2025, 1, 1),
            ended_on=date(2025, 12, 31),
        )

        admin_instance = MembershipAdmin(Membership, site)
        assert admin_instance.is_current(m_active) is True
        assert admin_instance.is_current(m_ended) is False

        # Test filter lookups
        request = RequestFactory().get("/admin/directory/membership/")
        filter_instance = CurrentMembershipFilter(
            request, {"is_current": ["current"]}, Membership, admin_instance
        )
        qs_current = filter_instance.queryset(request, Membership.objects.all())
        assert m_active in qs_current
        assert m_ended not in qs_current

        filter_instance_former = CurrentMembershipFilter(
            request, {"is_current": ["former"]}, Membership, admin_instance
        )
        qs_former = filter_instance_former.queryset(request, Membership.objects.all())
        assert m_ended in qs_former
        assert m_active not in qs_former


@pytest.mark.django_db
class TestPlatformsAdminFunctionality:
    """Verify custom admin methods and annotations for Platforms app."""

    def test_platform_admin_account_count(self):
        platform = Platform.objects.create(
            name="Kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
        )
        person = Person.objects.create(display_name="Streamer One")
        PlatformAccount.objects.create(
            person=person,
            platform=platform,
            handle="streamer1",
            url="https://kick.com/streamer1",
        )

        admin_instance = PlatformAdmin(Platform, site)
        request = RequestFactory().get("/admin/platforms/platform/")
        qs = admin_instance.get_queryset(request)
        annotated_platform = qs.get(id=platform.id)

        assert admin_instance.account_count(annotated_platform) == 1
