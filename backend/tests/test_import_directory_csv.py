"""Tests for the import_directory_csv management command."""

import tempfile
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.directory.models import (
    Faction,
    FactionStatus,
    Membership,
    MembershipRole,
    Person,
    PersonStatus,
)
from apps.platforms.models import Platform, PlatformAccount, PlatformKind


@pytest.fixture
def setup_platforms(db):
    """Ensure Kick and YouTube platform records exist."""
    kick, _ = Platform.objects.get_or_create(
        slug="kick",
        defaults={
            "name": "Kick",
            "kind": PlatformKind.LIVESTREAM,
            "supports_live": True,
        },
    )
    yt, _ = Platform.objects.get_or_create(
        slug="youtube",
        defaults={
            "name": "YouTube",
            "kind": PlatformKind.VIDEO,
            "supports_live": True,
        },
    )
    return {"kick": kick, "youtube": yt}


@pytest.mark.django_db
class TestImportDirectoryCsvCommand:
    def test_dry_run_does_not_modify_database(self, setup_platforms):
        csv_content = (
            "name,kick_url,youtube_url,role\n"
            "Test Member 1,https://kick.com/testmember1,https://youtube.com/@testmember1,member\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            out = StringIO()
            call_command("import_directory_csv", temp_path, "--dry-run", stdout=out)
            output = out.getvalue()

            assert "[DRY RUN REPORT]" in output
            assert "Creators:        1 created, 0 reused" in output
            assert "Validation: No errors or conflicts found." in output

            # Database MUST remain untouched
            assert not Person.objects.filter(display_name="Test Member 1").exists()
            assert not Faction.objects.filter(tag="TVA").exists()
            assert not PlatformAccount.objects.filter(handle="testmember1").exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_import_creates_records_and_subsequent_run_reuses_them(self, setup_platforms):
        csv_content = (
            "name,kick_url,youtube_url,role\n"
            "Alpha Creator,https://kick.com/alphakick,https://youtube.com/@alphayt,leader\n"
            "Beta Creator,https://kick.com/betakick,,member\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # First run: actual import
            out1 = StringIO()
            call_command("import_directory_csv", temp_path, stdout=out1)
            output1 = out1.getvalue()

            assert "[IMPORT REPORT]" in output1
            assert "Creators:        2 created, 0 reused" in output1
            assert "Memberships:     2 created, 0 reused" in output1
            assert "Platform Accounts:3 created, 0 reused" in output1

            # Check database records
            faction = Faction.objects.get(tag="TVA")
            assert faction.name == "THAKKUDU VAAVA ADHOLOKHAM"
            assert faction.status == FactionStatus.ACTIVE

            alpha = Person.objects.get(display_name="Alpha Creator")
            assert alpha.status == PersonStatus.PUBLISHED
            alpha_membership = Membership.objects.get(person=alpha, faction=faction)
            assert alpha_membership.role == MembershipRole.LEADER

            accounts = PlatformAccount.objects.filter(person=alpha)
            assert accounts.count() == 2

            # Second run: should reuse without creating duplicates
            out2 = StringIO()
            call_command("import_directory_csv", temp_path, stdout=out2)
            output2 = out2.getvalue()

            assert "Creators:        0 created, 2 reused" in output2
            assert "Memberships:     0 created, 2 reused" in output2
            assert "Platform Accounts:0 created, 3 reused" in output2

            creators = Person.objects.filter(
                display_name__in=["Alpha Creator", "Beta Creator"]
            )
            assert creators.count() == 2
            assert Membership.objects.filter(faction=faction).count() == 2
            assert PlatformAccount.objects.filter(person__in=creators).count() == 3
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_conflict_detection_aborts_import(self, setup_platforms):
        # Create existing person with kick account
        owner = Person.objects.create(
            display_name="Original Owner",
            status=PersonStatus.PUBLISHED,
        )
        PlatformAccount.objects.create(
            person=owner,
            platform=setup_platforms["kick"],
            handle="sharedkick",
            url="https://kick.com/sharedkick",
        )

        csv_content = (
            "name,kick_url\n"
            "Imposter,https://kick.com/sharedkick\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            out = StringIO()
            with pytest.raises(CommandError) as exc_info:
                call_command("import_directory_csv", temp_path, stdout=out)

            assert "Import aborted due to 1 error(s) / conflict(s)" in str(exc_info.value)
            assert "Already owned by 'Original Owner'" in out.getvalue()

            # Ensure Imposter was not saved (rolled back)
            assert not Person.objects.filter(display_name="Imposter").exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_does_not_overwrite_existing_non_empty_fields(self, setup_platforms):
        person = Person.objects.create(
            display_name="Existing Profile",
            bio="Original biography preserved",
            avatar_url="https://example.com/avatar.jpg",
            status=PersonStatus.PUBLISHED,
        )

        csv_content = (
            "name,kick_url,bio,avatar_url\n"
            "Existing Profile,https://kick.com/existingprofile,,\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            out = StringIO()
            call_command("import_directory_csv", temp_path, stdout=out)
            person.refresh_from_db()
            assert person.bio == "Original biography preserved"
            assert person.avatar_url == "https://example.com/avatar.jpg"
        finally:
            Path(temp_path).unlink(missing_ok=True)
