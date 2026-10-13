"""Management command to import directory creators, memberships, and platform accounts from CSV."""

import csv
import os
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.directory.models import (
    Faction,
    FactionStatus,
    Membership,
    MembershipRole,
    Person,
    PersonStatus,
)
from apps.platforms.models import Platform, PlatformAccount


class Command(BaseCommand):
    help = "Import gang members, profiles, and platform accounts from a directory CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to the CSV file to import.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Simulate the import without modifying the database.",
        )
        parser.add_argument(
            "--faction-name",
            type=str,
            default="THAKKUDU VAAVA ADHOLOKHAM",
            help="Name of the faction to assign members to (default: THAKKUDU VAAVA ADHOLOKHAM).",
        )
        parser.add_argument(
            "--faction-tag",
            type=str,
            default="TVA",
            help="Tag of the faction (default: TVA).",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        dry_run = options["dry_run"]
        faction_name = options["faction_name"].strip()
        faction_tag = options["faction_tag"].strip()

        if not os.path.isfile(csv_path):
            raise CommandError(f"CSV file not found at: {csv_path}")

        mode_label = "[DRY RUN]" if dry_run else "[IMPORT]"
        self.stdout.write(
            self.style.NOTICE(f"{mode_label} Starting directory CSV import from {csv_path}...")
        )

        with transaction.atomic():
            results = self._process_csv(
                csv_path=csv_path,
                faction_name=faction_name,
                faction_tag=faction_tag,
            )

            if dry_run:
                transaction.set_rollback(True)
                self._print_report(results, is_dry_run=True)
            elif results["errors"]:
                transaction.set_rollback(True)
                self._print_report(results, is_dry_run=False)
                raise CommandError(
                    f"Import aborted due to {len(results['errors'])} error(s) / conflict(s). "
                    "Database changes were rolled back."
                )
            else:
                self._print_report(results, is_dry_run=False)
                self.stdout.write(
                    self.style.SUCCESS("[IMPORT SUCCESS] Database successfully updated.")
                )

    def _process_csv(self, csv_path: str, faction_name: str, faction_tag: str) -> dict:
        results = {
            "faction": None,
            "faction_created": False,
            "creators_created": [],
            "creators_reused": [],
            "memberships_created": [],
            "memberships_reused": [],
            "accounts_created": [],
            "accounts_reused": [],
            "skipped_rows": [],
            "errors": [],
        }

        # 1. Resolve or create Faction
        faction = Faction.objects.filter(name=faction_name).first()
        if faction:
            results["faction"] = faction
            results["faction_created"] = False
            if faction_tag and not faction.tag:
                faction.tag = faction_tag
                faction.save(update_fields=["tag"])
        else:
            faction = Faction.objects.create(
                name=faction_name,
                tag=faction_tag,
                status=FactionStatus.ACTIVE,
            )
            results["faction"] = faction
            results["faction_created"] = True

        # 2. Build platform cache
        platforms = list(Platform.objects.all())
        platform_by_slug = {p.slug.lower(): p for p in platforms}
        platform_by_name = {p.name.lower(): p for p in platforms}

        # 3. Read and parse CSV
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                results["errors"].append("CSV file is empty or missing headers.")
                return results

            row_num = 1  # 1-based header is line 1, data starts line 2
            for raw_row in reader:
                row_num += 1
                row = {
                    (k.strip() if k else ""): (v.strip() if v else "")
                    for k, v in raw_row.items()
                    if k is not None
                }

                # Check for empty line
                if not any(row.values()):
                    results["skipped_rows"].append(f"Line {row_num}: Empty row skipped.")
                    continue

                display_name = (
                    row.get("name")
                    or row.get("creator_name")
                    or row.get("display_name")
                    or row.get("creator")
                    or row.get("member_name")
                    or row.get("streamer")
                    or ""
                ).strip()

                if not display_name:
                    results["errors"].append(
                        f"Line {row_num}: Missing creator name in row: {raw_row}"
                    )
                    continue

                # Role resolution
                role_val = (row.get("role") or "").strip().lower()
                valid_roles = {choice.value for choice in MembershipRole}
                role = role_val if role_val in valid_roles else MembershipRole.MEMBER

                # Optional metadata
                bio_val = (row.get("bio") or row.get("description") or "").strip()
                avatar_val = (row.get("avatar_url") or row.get("avatar") or "").strip()

                # A. Creator (Person) record
                person = Person.objects.filter(display_name__iexact=display_name).first()
                if person:
                    results["creators_reused"].append(person.display_name)
                    updated_fields = []
                    if bio_val and not person.bio:
                        person.bio = bio_val
                        updated_fields.append("bio")
                    if avatar_val and not person.avatar_url:
                        person.avatar_url = avatar_val
                        updated_fields.append("avatar_url")
                    if person.status != PersonStatus.PUBLISHED:
                        person.status = PersonStatus.PUBLISHED
                        updated_fields.append("status")
                    if updated_fields:
                        person.save(update_fields=updated_fields)
                else:
                    person = Person.objects.create(
                        display_name=display_name,
                        bio=bio_val,
                        avatar_url=avatar_val,
                        status=PersonStatus.PUBLISHED,
                    )
                    results["creators_created"].append(person.display_name)

                # B. Membership record
                membership = Membership.objects.filter(
                    person=person,
                    faction=faction,
                    ended_on__isnull=True,
                ).first()
                if membership:
                    results["memberships_reused"].append(f"{display_name} -> {faction.tag}")
                else:
                    membership = Membership.objects.create(
                        person=person,
                        faction=faction,
                        role=role,
                        started_on=timezone.now().date(),
                        ended_on=None,
                    )
                    results["memberships_created"].append(
                        f"{display_name} -> {faction.tag} ({role})"
                    )

                # C. Extract Platform Accounts
                account_entries = self._extract_platform_entries(row)

                for plat_hint, raw_url, explicit_handle in account_entries:
                    if not raw_url:
                        continue

                    # Validate URL structure and resolve platform
                    clean_url, platform = self._resolve_url_and_platform(
                        raw_url=raw_url,
                        plat_hint=plat_hint,
                        platform_by_slug=platform_by_slug,
                        platform_by_name=platform_by_name,
                    )

                    if not platform:
                        results["errors"].append(
                            f"Line {row_num}: Could not resolve platform for URL "
                            f"'{raw_url}' (hint: '{plat_hint}')"
                        )
                        continue

                    # Parse handle / external_id
                    handle, external_id = self._parse_account_identifier(
                        url=clean_url,
                        platform=platform,
                        explicit_handle=explicit_handle,
                    )

                    if not handle and not external_id:
                        results["errors"].append(
                            f"Line {row_num}: Could not extract handle or external_id "
                            f"from URL '{raw_url}' for {platform.name}"
                        )
                        continue

                    # Check for conflicting ownership
                    conflict_error = self._check_account_conflict(
                        person=person,
                        platform=platform,
                        handle=handle,
                        external_id=external_id,
                        line_num=row_num,
                    )
                    if conflict_error:
                        results["errors"].append(conflict_error)
                        continue

                    # Resolve existing account or create new
                    existing_acc = self._find_existing_account(
                        person=person,
                        platform=platform,
                        handle=handle,
                        external_id=external_id,
                        url=clean_url,
                    )

                    if existing_acc:
                        results["accounts_reused"].append(
                            f"{person.display_name} @ {platform.name} ({handle or external_id})"
                        )
                        if clean_url and existing_acc.url != clean_url:
                            existing_acc.url = clean_url
                            existing_acc.save(update_fields=["url"])
                    else:
                        account = PlatformAccount(
                            person=person,
                            platform=platform,
                            handle=handle,
                            external_id=external_id,
                            url=clean_url,
                        )
                        try:
                            account.full_clean()
                            account.save()
                            results["accounts_created"].append(
                                f"{person.display_name} @ {platform.name} ({handle or external_id})"
                            )
                        except ValidationError as ve:
                            results["errors"].append(
                                f"Line {row_num}: Validation error saving account "
                                f"for '{person.display_name}': {ve}"
                            )

        return results

    def _extract_platform_entries(self, row: dict) -> list[tuple[str, str, str]]:
        """Extract all potential (platform_hint, url, explicit_handle) tuples from a CSV row.

        Supports:
        - Tall schema: 'platform' and 'url' (or 'link') columns
        - Wide schema: 'kick', 'kick_url', 'youtube', 'youtube_url', etc.
        - Direct URL without platform column
        """
        entries = []
        platform_col = (row.get("platform") or "").strip()
        url_col = (row.get("url") or row.get("link") or "").strip()
        handle_col = (row.get("handle") or "").strip()

        if url_col:
            entries.append((platform_col, url_col, handle_col))

        # Check for wide platform columns
        reserved_keys = {
            "name",
            "creator_name",
            "display_name",
            "creator",
            "member_name",
            "streamer",
            "role",
            "bio",
            "description",
            "avatar_url",
            "avatar",
            "faction",
            "platform",
            "url",
            "link",
            "handle",
            "notes",
        }

        for key, val in row.items():
            if not key or not val:
                continue
            norm_key = key.lower().strip()
            val_str = str(val).strip()
            if norm_key in reserved_keys or not val_str:
                continue

            # Check if this column specifies kick/youtube or similar
            if norm_key.endswith("_url") or norm_key.endswith("_link"):
                plat = norm_key.replace("_url", "").replace("_link", "").strip()
                entries.append((plat, val_str, ""))
            elif norm_key in {"kick", "youtube", "twitch", "x", "twitter", "instagram", "tiktok"}:
                entries.append((norm_key, val_str, ""))

        return entries

    def _resolve_url_and_platform(
        self,
        raw_url: str,
        plat_hint: str,
        platform_by_slug: dict,
        platform_by_name: dict,
    ) -> tuple[str, Platform | None]:
        """Normalize URL and resolve Platform model instance."""
        url_str = raw_url.strip()
        if not url_str.startswith("http://") and not url_str.startswith("https://"):
            url_str = "https://" + url_str

        parsed = urlparse(url_str)
        netloc = parsed.netloc.lower()

        # 1. Match from explicit hint
        if plat_hint:
            norm_hint = plat_hint.lower().strip()
            if norm_hint in platform_by_slug:
                return url_str, platform_by_slug[norm_hint]
            if norm_hint in platform_by_name:
                return url_str, platform_by_name[norm_hint]

        # 2. Match from URL domain
        if "kick.com" in netloc:
            return url_str, platform_by_slug.get("kick") or platform_by_name.get("kick")
        if "youtube.com" in netloc or "youtu.be" in netloc:
            return url_str, platform_by_slug.get("youtube") or platform_by_name.get("youtube")

        return url_str, None

    def _parse_account_identifier(
        self,
        url: str,
        platform: Platform,
        explicit_handle: str = "",
    ) -> tuple[str, str]:
        """Extract handle and external_id from URL and platform rules."""
        if explicit_handle:
            clean_handle = explicit_handle.strip().lstrip("@")
            return clean_handle, ""

        parsed = urlparse(url)
        path = parsed.path.strip("/")
        segments = [s for s in path.split("/") if s]

        handle = ""
        external_id = ""

        plat_slug = platform.slug.lower() if platform.slug else platform.name.lower()

        if plat_slug == "kick":
            if segments:
                handle = segments[0].strip()
        elif plat_slug == "youtube":
            if segments:
                first = segments[0]
                if first.startswith("@"):
                    handle = first.lstrip("@").strip()
                elif first == "channel" and len(segments) > 1:
                    external_id = segments[1].strip()
                elif first in {"c", "user"} and len(segments) > 1:
                    handle = segments[1].strip()
                else:
                    handle = first.lstrip("@").strip()
        else:
            if segments:
                handle = segments[0].lstrip("@").strip()

        return handle, external_id

    def _check_account_conflict(
        self,
        person: Person,
        platform: Platform,
        handle: str,
        external_id: str,
        line_num: int,
    ) -> str | None:
        """Verify whether the account belongs to another person."""
        existing = None
        if handle:
            existing = (
                PlatformAccount.objects.filter(
                    platform=platform,
                    handle__iexact=handle,
                )
                .select_related("person")
                .first()
            )
        elif external_id:
            existing = (
                PlatformAccount.objects.filter(
                    platform=platform,
                    external_id=external_id,
                )
                .select_related("person")
                .first()
            )

        if existing and existing.person_id != person.id:
            ident = handle or external_id
            return (
                f"Line {line_num}: Account ownership conflict for '{ident}' on {platform.name}. "
                f"Already owned by '{existing.person.display_name}' (ID: {existing.person_id}), "
                f"cannot reassign to '{person.display_name}' (ID: {person.id})."
            )

        return None

    def _find_existing_account(
        self,
        person: Person,
        platform: Platform,
        handle: str,
        external_id: str,
        url: str,
    ) -> PlatformAccount | None:
        """Find an existing platform account for the same person."""
        if handle:
            acc = PlatformAccount.objects.filter(
                person=person,
                platform=platform,
                handle__iexact=handle,
            ).first()
            if acc:
                return acc

        if external_id:
            acc = PlatformAccount.objects.filter(
                person=person,
                platform=platform,
                external_id=external_id,
            ).first()
            if acc:
                return acc

        return PlatformAccount.objects.filter(
            person=person,
            platform=platform,
            url=url,
        ).first()

    def _print_report(self, results: dict, is_dry_run: bool):
        """Display formatted statistics and validation errors."""
        header = "[DRY RUN REPORT]" if is_dry_run else "[IMPORT REPORT]"
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.MIGRATE_HEADING(header))
        self.stdout.write("=" * 60)

        faction = results["faction"]
        if faction:
            f_status = "Would Create" if is_dry_run and results["faction_created"] else (
                "Created" if results["faction_created"] else "Reused"
            )
            self.stdout.write(f"Faction: [{faction.tag}] {faction.name} ({f_status})")

        self.stdout.write(
            f"Creators:        {len(results['creators_created'])} created, "
            f"{len(results['creators_reused'])} reused"
        )
        self.stdout.write(
            f"Memberships:     {len(results['memberships_created'])} created, "
            f"{len(results['memberships_reused'])} reused"
        )
        self.stdout.write(
            f"Platform Accounts:{len(results['accounts_created'])} created, "
            f"{len(results['accounts_reused'])} reused"
        )

        if results["skipped_rows"]:
            self.stdout.write(
                self.style.WARNING(f"\nSkipped Rows ({len(results['skipped_rows'])}):")
            )
            for s in results["skipped_rows"]:
                self.stdout.write(f"  - {s}")

        if results["errors"]:
            self.stdout.write(
                self.style.ERROR(f"\nErrors / Conflicts Encountered ({len(results['errors'])}):")
            )
            for err in results["errors"]:
                self.stdout.write(self.style.ERROR(f"  ! {err}"))
        else:
            self.stdout.write(self.style.SUCCESS("\nValidation: No errors or conflicts found."))
        self.stdout.write("=" * 60)
