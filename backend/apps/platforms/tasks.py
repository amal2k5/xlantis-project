from celery import shared_task

from apps.platforms.models import PlatformAccount
from apps.platforms.services.kick import KickAPIError
from apps.platforms.services.live_tracker import sync_kick_account


@shared_task
def sync_all_kick_accounts():
    """Synchronize live status for registered Kick accounts."""
    accounts = PlatformAccount.objects.filter(
        platform__slug__iexact="kick",
        platform__is_active=True,
    ).select_related("platform")

    results = {
        "checked": 0,
        "updated": 0,
        "failed": 0,
    }

    for account in accounts:
        results["checked"] += 1

        try:
            sync_kick_account(account)
            results["updated"] += 1
        except (KickAPIError, ValueError) as exc:
            results["failed"] += 1
            print(f"Kick sync failed for {account.handle}: {exc}")

    return results
