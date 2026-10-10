from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.directory.slugs import generate_unique_slug


class Category(models.Model):
    """Category classification for persons (e.g. Gang Member, Citizen, Content Creator)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class PersonStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    HIDDEN = "hidden", "Hidden"


class Person(models.Model):
    """Represents an individual directory profile."""

    display_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PersonStatus.choices,
        default=PersonStatus.DRAFT,
        db_index=True,
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    categories = models.ManyToManyField(
        Category,
        related_name="persons",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "display_name"]
        verbose_name = "Person"
        verbose_name_plural = "Persons"
        indexes = [
            models.Index(fields=["status", "-is_featured"], name="person_status_featured_idx"),
        ]

    def __str__(self) -> str:
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.slug:
            generate_unique_slug(self, self.display_name)
        super().save(*args, **kwargs)


class FactionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    DISBANDED = "disbanded", "Disbanded"


class Faction(models.Model):
    """Represents an actual gang or organization."""

    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    tag = models.CharField(max_length=15, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=FactionStatus.choices,
        default=FactionStatus.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Faction"
        verbose_name_plural = "Factions"

    def __str__(self) -> str:
        if self.tag:
            return f"[{self.tag}] {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class MembershipRole(models.TextChoices):
    LEADER = "leader", "Leader"
    MEMBER = "member", "Member"
    PROSPECT = "prospect", "Prospect"
    AFFILIATE = "affiliate", "Affiliate"


class Membership(models.Model):
    """Connects Person and Faction, supporting current and historical memberships."""

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    faction = models.ForeignKey(
        Faction,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
    )
    started_on = models.DateField(default=timezone.now)
    ended_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-started_on"]
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"
        constraints = [
            # Prevent more than one current (ended_on IS NULL) membership
            # for the same Person + Faction
            models.UniqueConstraint(
                fields=["person", "faction"],
                condition=models.Q(ended_on__isnull=True),
                name="unique_current_person_faction_membership",
            ),
            # Ensure ended_on >= started_on when ended_on is specified
            models.CheckConstraint(
                condition=models.Q(ended_on__isnull=True)
                | models.Q(ended_on__gte=models.F("started_on")),
                name="membership_ended_after_started",
            ),
        ]

    def __str__(self) -> str:
        status_text = "Current" if self.ended_on is None else f"Ended {self.ended_on}"
        return f"{self.person.display_name} - {self.faction.name} ({self.role}, {status_text})"

    def clean(self):
        super().clean()
        if self.ended_on and self.started_on and self.ended_on < self.started_on:
            raise ValidationError(
                {"ended_on": "The end date cannot be earlier than the start date."}
            )
