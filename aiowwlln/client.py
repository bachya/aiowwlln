"""Define a client to interact with the WWLLN."""
from datetime import timedelta
import json
import logging
import time

from aiocache import cached
from aiohttp import ClientSession, client_exceptions

from .errors import RequestError
from .helpers.geo import haversine

_LOGGER = logging.getLogger(__name__)

DATA_URL = "http://wwlln.net/new/map/data/current.json"

DEFAULT_CACHE_KEY = "lightning_strike_data"
DEFAULT_CACHE_SECONDS = 60


class Client:
    """Define the client."""

    def __init__(
        self, websession: ClientSession, *, cache_seconds: int = DEFAULT_CACHE_SECONDS
    ) -> None:
        """Initialize."""
        # Since this library is built on an unofficial data source, let's be responsible
        # citizens and not allow updates faster than every 60 seconds:
        if cache_seconds < DEFAULT_CACHE_SECONDS:
            _LOGGER.warning(
                "Setting cache timeout to lowest allowed: %s seconds",
                DEFAULT_CACHE_SECONDS,
            )
            cache_seconds = DEFAULT_CACHE_SECONDS

        self._websession = websession
        self.dump = cached(key=DEFAULT_CACHE_KEY, ttl=cache_seconds)(self._dump)

    async def _dump(self) -> dict:
        """Return raw lightning strike data from the WWLLN."""
        return await self.request("get", DATA_URL)

    async def request(
        self, method: str, url: str, *, headers: dict = None, params: dict = None
    ) -> dict:
        """Make an HTTP request."""
        async with self._websession.request(
            method, url, headers=headers, params=params
        ) as resp:
            try:
                resp.raise_for_status()
                return await resp.json(content_type=None)
            except client_exceptions.ClientError as err:
                raise RequestError(
                    "Error requesting data from {0}: {1}".format(url, err)
                ) from None
            except json.decoder.JSONDecodeError:
                raise RequestError("Invalid JSON found from {0}".format(url))

    async def within_radius(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        *,
        unit: str = "metric",
        window: timedelta = None
    ) -> dict:
        """
        Get a dict of strike IDs/strikes within a radius around a lat. and long.

        Optionally provide a window of time to restrict results to.
        """
        if unit not in ("imperial", "metric"):
            raise ValueError('Unit must be either "imperial" or "metric"')

        all_strikes = await self.dump()

        nearby_strikes = {}
        for strike_id, strike in all_strikes.items():
            distance = haversine(
                latitude, longitude, strike["lat"], strike["long"], unit=unit
            )
            if distance <= radius and (
                not window or time.time() - strike["unixTime"] <= window.total_seconds()
            ):
                strike["distance"] = distance
                nearby_strikes[strike_id] = strike

        return nearby_strikes
