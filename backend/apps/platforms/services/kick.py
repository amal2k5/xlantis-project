import requests
from django.conf import settings
from django.core.cache import cache


class KickAPIError(Exception):
    """Raised when a Kick API request fails."""


class KickClient:
    TOKEN_CACHE_KEY = "kick_app_access_token"
    TOKEN_URL = settings.KICK_TOKEN_URL
    API_BASE_URL = settings.KICK_API_BASE_URL
    TIMEOUT = 15

    def _get_access_token(self):
        token = cache.get(self.TOKEN_CACHE_KEY)

        if token:
            return token

        if not settings.KICK_CLIENT_ID or not settings.KICK_CLIENT_SECRET:
            raise KickAPIError("Kick API credentials are not configured.")

        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.KICK_CLIENT_ID,
                    "client_secret": settings.KICK_CLIENT_SECRET,
                },
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise KickAPIError("Could not authenticate with Kick.") from exc

        token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))

        if not token:
            raise KickAPIError("Kick did not return an access token.")

        # Expire the cached token slightly before its actual expiry.
        cache.set(self.TOKEN_CACHE_KEY, token, max(1, expires_in - 60))

        return token

    def get_channel(self, slug):
        if not slug or not slug.strip():
            raise ValueError("A Kick channel slug is required.")

        try:
            response = requests.get(
                f"{self.API_BASE_URL}/channels",
                params={"slug": slug.strip()},
                headers={
                    "Authorization": f"Bearer {self._get_access_token()}",
                },
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise KickAPIError(
                f"Could not retrieve Kick channel '{slug}'."
            ) from exc

        channels = payload.get("data", [])

        if not channels:
            return None

        return channels[0]
