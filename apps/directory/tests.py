from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

from apps.directory.models import (
    Category,
    Faction,
    FactionStatus,
    Membership,
    MembershipRole,
    Person,
    PersonStatus,
)


@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation_and_slug(self):
        cat = Category.objects.create(name="Gang Member")
        assert cat.slug == "gang-member"
        assert str(cat) == "Gang Member"
        assert cat.is_active is True

    def test_category_name_unique(self):
        Category.objects.create(name="Citizen")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Citizen")


@pytest.mark.django_db
class TestPersonModel:
    def test_slug_generation_and_preservation(self):
        p1 = Person.objects.create(display_name="Dark Knight")
        assert p1.slug == "dark-knight"
        assert str(p1) == "Dark Knight"

        # Slug must not change when display_name changes
        p1.display_name = "Bright Knight"
        p1.save()
        p1.refresh_from_db()
        assert p1.slug == "dark-knight"

    def test_slug_collision_handling(self):
        p1 = Person.objects.create(display_name="Dark Knight")
        p2 = Person.objects.create(display_name="Dark Knight")
        p3 = Person.objects.create(display_name="Dark Knight")

        assert p1.slug == "dark-knight"
        assert p2.slug == "dark-knight-2"
        assert p3.slug == "dark-knight-3"

    def test_person_category_relationship(self):
        cat1 = Category.objects.create(name="Gang Member")
        cat2 = Category.objects.create(name="Content Creator")
        person = Person.objects.create(
            display_name="Roleplayer One",
            status=PersonStatus.PUBLISHED,
            is_featured=True,
        )
        person.categories.add(cat1, cat2)

        assert person.categories.count() == 2
        assert person in cat1.persons.all()
        assert person in cat2.persons.all()


@pytest.mark.django_db
class TestFactionAndMembershipModel:
    def test_faction_creation_and_slug(self):
        faction = Faction.objects.create(
            name="The Syndicate",
            tag="SYN",
            status=FactionStatus.ACTIVE,
        )
        assert faction.slug == "the-syndicate"
        assert str(faction) == "[SYN] The Syndicate"

    def test_membership_creation_and_current(self):
        person = Person.objects.create(display_name="Player One")
        faction = Faction.objects.create(name="Redline Racers", tag="RLR")

        membership = Membership.objects.create(
            person=person,
            faction=faction,
            role=MembershipRole.LEADER,
            started_on=date(2026, 1, 1),
        )
        assert membership.ended_on is None
        assert "Current" in str(membership)
        assert membership in person.memberships.all()
        assert membership in faction.memberships.all()

    def test_duplicate_current_membership_prevented(self):
        person = Person.objects.create(display_name="Player Two")
        faction = Faction.objects.create(name="Night Owls", tag="OWL")

        Membership.objects.create(
            person=person,
            faction=faction,
            role=MembershipRole.MEMBER,
            started_on=date(2026, 1, 1),
        )

        # Attempting a second active membership for the same person + faction must fail
        with pytest.raises(IntegrityError):
            Membership.objects.create(
                person=person,
                faction=faction,
                role=MembershipRole.PROSPECT,
                started_on=date(2026, 3, 1),
            )

    def test_historical_membership_and_rejoining(self):
        person = Person.objects.create(display_name="Player Three")
        faction = Faction.objects.create(name="Iron Clad", tag="IC")

        # First stint (past)
        past_membership = Membership.objects.create(
            person=person,
            faction=faction,
            role=MembershipRole.PROSPECT,
            started_on=date(2025, 1, 1),
            ended_on=date(2025, 6, 1),
        )
        assert past_membership.ended_on is not None

        # Second stint (later rejoined, now current)
        current_membership = Membership.objects.create(
            person=person,
            faction=faction,
            role=MembershipRole.MEMBER,
            started_on=date(2026, 1, 1),
            ended_on=None,
        )
        assert current_membership.ended_on is None
        assert person.memberships.count() == 2

    def test_ended_on_before_started_on_validation(self):
        person = Person.objects.create(display_name="Player Four")
        faction = Faction.objects.create(name="Viper Squad", tag="VS")

        membership = Membership(
            person=person,
            faction=faction,
            started_on=date(2026, 5, 10),
            ended_on=date(2026, 5, 1),
        )
        with pytest.raises(ValidationError):
            membership.clean()

    def test_deletion_protection(self):
        person = Person.objects.create(display_name="Player Five")
        faction = Faction.objects.create(name="Ghost Riders", tag="GR")
        Membership.objects.create(person=person, faction=faction)

        # Deleting person or faction must be blocked by ProtectedError
        with pytest.raises(ProtectedError):
            person.delete()

        with pytest.raises(ProtectedError):
            faction.delete()
