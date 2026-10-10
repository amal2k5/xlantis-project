from django.utils.text import slugify


def generate_unique_slug(instance, source_text: str, slug_field: str = "slug") -> str:
    """Generate a unique slug for a model instance if not already set.

    - Preserves existing slugs (does not overwrite on update).
    - Automatically handles collisions by appending -2, -3, etc.
    """
    current_val = getattr(instance, slug_field, None)
    if current_val:
        return current_val

    base_slug = slugify(source_text) or "item"
    candidate = base_slug
    counter = 2

    model_class = instance.__class__
    qs = model_class.objects.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)

    while qs.filter(**{slug_field: candidate}).exists():
        candidate = f"{base_slug}-{counter}"
        counter += 1

    setattr(instance, slug_field, candidate)
    return candidate
