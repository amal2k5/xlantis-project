from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower

from apps.directory.slugs import generate_unique_slug


class PlatformKind(models.TextChoices):
    LIVESTREAM = "livestream", "Livestream"
    VIDEO = "video", "Video"
    SOCIAL = "social", "Social"
    OTHER = "other", "Other"


class Platform(models.Model):
    """Represents an external platform (e.g. Kick, YouTube, Instagram, TikTok, X)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    kind = models.CharField(
        max_length=20,
        choices=PlatformKind.choices,
        default=PlatformKind.OTHER,
    )
    supports_live = models.BooleanField(default=False)
    url_template = models.CharField(
        max_length=255,
        blank=True,
        help_text="URL template supporting {handle} or {external_id}",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class PlatformAccount(models.Model):
    """Connects Person to Platform for links, handles, and verification."""

    person = models.ForeignKey(
        "directory.Person",
        on_delete=models.PROTECT,
        related_name="platform_accounts",
    )
    platform = models.ForeignKey(
        Platform,
        on_delete=models.PROTECT,
        related_name="accounts",
    )
    handle = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=100, blank=True)
    url = models.URLField(max_length=500)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["platform", "handle"]
        verbose_name = "Platform Account"
        verbose_name_plural = "Platform Accounts"
        constraints = [
            # At least one of handle or external_id must be provided
            models.CheckConstraint(
                condition=~models.Q(handle="") | ~models.Q(external_id=""),
                name="platform_account_handle_or_external_id_required",
            ),
            # Case-insensitive uniqueness for (platform, Lower('handle')) when handle is provided
            models.UniqueConstraint(
                Lower("handle"),
                "platform",
                condition=~models.Q(handle=""),
                name="unique_platform_lower_handle",
            ),
            # Uniqueness for (platform, external_id) when external_id is provided
            models.UniqueConstraint(
                fields=["platform", "external_id"],
                condition=~models.Q(external_id=""),
                name="unique_platform_external_id",
            ),
        ]

    def __str__(self) -> str:
        identifier = self.handle or self.external_id
        return f"{self.person.display_name} @ {self.platform.name} ({identifier})"

    def save(self, *args, **kwargs):
        if self.handle:
            self.handle = self.handle.strip()
        if self.external_id:
            self.external_id = self.external_id.strip()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        normalized_handle = (self.handle or "").strip()
        normalized_external_id = (self.external_id or "").strip()
        if not normalized_handle and not normalized_external_id:
            raise ValidationError(
                "At least one of handle or external_id must be provided for a platform account."
            )



class PlatformLiveStatus(models.Model):
    """Stores the latest livestream status for a platform account."""

    platform_account = models.OneToOneField(
        PlatformAccount,
        on_delete=models.CASCADE,
        related_name="live_status",
    )

    is_live = models.BooleanField(default=False, db_index=True)
    stream_title = models.CharField(max_length=255, blank=True)
    viewer_count = models.PositiveIntegerField(default=0)

    stream_started_at = models.DateTimeField(null=True, blank=True)
    last_seen_live_at = models.DateTimeField(null=True, blank=True)
    last_stream_ended_at = models.DateTimeField(null=True, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Platform Live Status"
        verbose_name_plural = "Platform Live Statuses"

    def __str__(self):
        status = "LIVE" if self.is_live else "OFFLINE"
        return f"{self.platform_account} - {status}"
