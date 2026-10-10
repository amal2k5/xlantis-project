import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

from apps.directory.models import Person
from apps.platforms.models import Platform, PlatformAccount, PlatformKind


@pytest.mark.django_db
class TestPlatformModel:
    def test_platform_creation_and_slug(self):
        platform = Platform.objects.create(
            name="Kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
            url_template="https://kick.com/{handle}",
        )
        assert platform.slug == "kick"
        assert str(platform) == "Kick"
        assert platform.supports_live is True

    def test_platform_name_uniqueness(self):
        Platform.objects.create(name="YouTube")
        with pytest.raises(IntegrityError):
            Platform.objects.create(name="YouTube")

    def test_platform_slug_collision_handling(self):
        p1 = Platform.objects.create(name="Twitch Live")
        p2 = Platform.objects.create(name="Twitch-Live")

        assert p1.slug == "twitch-live"
        assert p2.slug == "twitch-live-2"


@pytest.mark.django_db
class TestPlatformAccountModel:
    @pytest.fixture
    def setup_data(self):
        person = Person.objects.create(display_name="Streamer One")
        kick = Platform.objects.create(
            name="Kick",
            kind=PlatformKind.LIVESTREAM,
            supports_live=True,
        )
        yt = Platform.objects.create(
            name="YouTube",
            kind=PlatformKind.VIDEO,
        )
        return {"person": person, "kick": kick, "yt": yt}

    def test_create_multiple_platform_accounts_for_one_person(self, setup_data):
        person = setup_data["person"]
        kick = setup_data["kick"]
        yt = setup_data["yt"]

        acc1 = PlatformAccount.objects.create(
            person=person,
            platform=kick,
            handle="Streamer1",
            url="https://kick.com/Streamer1",
        )
        acc2 = PlatformAccount.objects.create(
            person=person,
            platform=yt,
            handle="Streamer1YT",
            url="https://youtube.com/@Streamer1YT",
        )

        assert person.platform_accounts.count() == 2
        assert acc1 in person.platform_accounts.all()
        assert acc2 in person.platform_accounts.all()
        assert str(acc1) == "Streamer One @ Kick (Streamer1)"

    def test_validation_requires_handle_or_external_id(self, setup_data):
        person = setup_data["person"]
        kick = setup_data["kick"]

        # Neither handle nor external_id provided
        account = PlatformAccount(
            person=person,
            platform=kick,
            handle="",
            external_id="",
            url="https://kick.com/unknown",
        )
        # Model level clean validation
        with pytest.raises(ValidationError):
            account.full_clean()

        # Database check constraint enforcement
        with pytest.raises(IntegrityError):
            account.save()

    def test_case_insensitive_handle_uniqueness_on_same_platform(self, setup_data):
        person1 = setup_data["person"]
        person2 = Person.objects.create(display_name="Streamer Two")
        kick = setup_data["kick"]

        PlatformAccount.objects.create(
            person=person1,
            platform=kick,
            handle="GamerPro",
            url="https://kick.com/GamerPro",
        )

        # Attempt to create with lower case 'gamerpro' on same platform Kick must fail
        with pytest.raises(IntegrityError):
            PlatformAccount.objects.create(
                person=person2,
                platform=kick,
                handle="gamerpro",
                url="https://kick.com/gamerpro",
            )

    def test_same_handle_on_different_platforms_allowed(self, setup_data):
        person = setup_data["person"]
        kick = setup_data["kick"]
        yt = setup_data["yt"]

        acc_kick = PlatformAccount.objects.create(
            person=person,
            platform=kick,
            handle="GamerPro",
            url="https://kick.com/GamerPro",
        )
        acc_yt = PlatformAccount.objects.create(
            person=person,
            platform=yt,
            handle="GamerPro",
            url="https://youtube.com/@GamerPro",
        )
        assert acc_kick.pk is not None
        assert acc_yt.pk is not None

    def test_external_id_uniqueness_on_same_platform(self, setup_data):
        person1 = setup_data["person"]
        person2 = Person.objects.create(display_name="Streamer Three")
        yt = setup_data["yt"]

        PlatformAccount.objects.create(
            person=person1,
            platform=yt,
            external_id="UC_123456789",
            url="https://youtube.com/channel/UC_123456789",
        )

        with pytest.raises(IntegrityError):
            PlatformAccount.objects.create(
                person=person2,
                platform=yt,
                external_id="UC_123456789",
                url="https://youtube.com/channel/UC_123456789",
            )

    def test_deletion_protection(self, setup_data):
        person = setup_data["person"]
        kick = setup_data["kick"]

        PlatformAccount.objects.create(
            person=person,
            platform=kick,
            handle="ProtectedUser",
            url="https://kick.com/ProtectedUser",
        )

        # Deleting person or platform must be protected
        with pytest.raises(ProtectedError):
            person.delete()

        with pytest.raises(ProtectedError):
            kick.delete()
