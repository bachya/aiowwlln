"""Define a client to interact with the WWLLN."""
import asyncio
from datetime import timedelta
import json
import logging
import time
from typing import Callable, Dict

from aiocache import cached
from aiohttp import ClientSession, client_exceptions

from .errors import RequestError
from .helpers.geo import haversine

_LOGGER: logging.Logger = logging.getLogger(__name__)

DATA_URL: str = "http://wwlln.net/new/map/data/current.json"

DEFAULT_CACHE_KEY: str = "lightning_strike_data"
DEFAULT_CACHE_SECONDS: int = 60
DEFAULT_RETRY_DELAY: int = 3


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

        self._currently_retrying: bool = False
        self._websession: ClientSession = websession
        self.dump: Callable = cached(key=DEFAULT_CACHE_KEY, ttl=cache_seconds)(
            self._dump
        )

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
                data: dict = await resp.json(content_type=None)
                self._currently_retrying = False
                return data
            except (client_exceptions.ClientError, json.decoder.JSONDecodeError) as err:
                if self._currently_retrying:
                    raise RequestError(f"Recurring request error from {url}: {err}")

                self._currently_retrying = True
                _LOGGER.info(
                    "Error during request; waiting %s seconds before trying again",
                    DEFAULT_RETRY_DELAY,
                )
                await asyncio.sleep(DEFAULT_RETRY_DELAY)
                return await self.request(method, url, headers=headers, params=params)

    async def within_radius(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        *,
        unit: str = "metric",
        window: timedelta = None,
    ) -> dict:
        """
        Get a dict of strike IDs/strikes within a radius around a lat. and long.

        Optionally provide a window of time to restrict results to.
        """
        if unit not in ("imperial", "metric"):
            raise ValueError('Unit must be either "imperial" or "metric"')

        all_strikes: dict = await self.dump()

        nearby_strikes: Dict[str, dict] = {}
        strike_id: str
        strike: dict
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
