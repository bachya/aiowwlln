"""Define a client to interact with the WWLLN."""
from aiohttp import ClientSession, client_exceptions

from .errors import RequestError
from .helpers.geo import get_nearest_by_coordinates, haversine

DATA_URL = "http://wwlln.net/new/map/data/current.json"


class Client:
    """Define the client."""

    def __init__(self, websession: ClientSession) -> None:
        """Initialize."""
        self._websession = websession

    async def dump(self) -> dict:
        """Return raw lightning strike data from the WWLLN."""
        return await self.request("get", DATA_URL)

    async def nearest(self, latitude: float, longitude: float) -> dict:
        """Get the nearest strike to a set of coordinates."""
        all_strikes = await self.dump()
        nearest_strike = get_nearest_by_coordinates(
            list(all_strikes.values()), "lat", "long", latitude, longitude
        )

        nearest_strike["distance"] = haversine(
            latitude, longitude, nearest_strike["lat"], nearest_strike["long"]
        )

        return nearest_strike

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

    async def within_radius(
        self, latitude: float, longitude: float, radius: float, *, unit: str = "metric"
    ) -> list:
        """Get a list of strikes within a radius around a set of coordinates."""
        if unit not in ("imperial", "metric"):
            raise ValueError('Unit must be either "imperial" or "metric"')

        all_strikes = await self.dump()

        nearby_strikes = []
        for strike in all_strikes.values():
            distance = haversine(
                latitude, longitude, strike["lat"], strike["long"], unit=unit
            )
            if distance <= radius:
                strike["distance"] = distance
                nearby_strikes.append(strike)

        return nearby_strikes