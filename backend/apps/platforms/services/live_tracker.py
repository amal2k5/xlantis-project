from django.utils import timezone

from apps.platforms.models import PlatformAccount, PlatformLiveStatus
from apps.platforms.services.kick import KickAPIError, KickClient


def sync_kick_account(account: PlatformAccount) -> PlatformLiveStatus:
    """
    Fetch a Kick channel's current status and update its database record.
    """
    if account.platform.slug.lower() != "kick":
        raise ValueError("The platform account must belong to Kick.")

    if not account.handle:
        raise ValueError("The Kick account has no channel handle.")

    client = KickClient()
    channel = client.get_channel(account.handle)

    if channel is None:
        raise KickAPIError(
            f"Kick channel '{account.handle}' was not found."
        )

    stream = channel.get("stream") or {}
    is_live = bool(stream.get("is_live"))
    now = timezone.now()

    status, _ = PlatformLiveStatus.objects.get_or_create(
        platform_account=account,
    )

    # Update live/offline transition timestamps.
    if is_live:
        status.last_seen_live_at = now

        if not status.is_live:
            status.last_stream_ended_at = None

        status.stream_started_at = stream.get("start_time")
        status.stream_title = channel.get("stream_title") or ""
        status.viewer_count = stream.get("viewer_count") or 0

    else:
        if status.is_live:
            status.last_stream_ended_at = now

        status.viewer_count = 0

    status.is_live = is_live
    status.last_checked_at = now
    status.save()

    return status