"""Define tests for the client object."""
# pylint: disable=redefined-outer-name,unused-import
import json

from aiocache import SimpleMemoryCache
import aiohttp
import pytest

from aiowwlln import Client
from aiowwlln.errors import RequestError

from aiowwlln.client import DEFAULT_CACHE_KEY
from .const import (
    TEST_LATITUDE,
    TEST_LONGITUDE,
    TEST_RADIUS_IMPERIAL,
    TEST_RADIUS_METRIC,
)
from .fixtures.client import fixture_dump_json, fixture_dump_invalid_json  # noqa


@pytest.mark.asyncio
async def test_bad_request(aresponses, event_loop):
    """Test that the proper exception is raised during a bad request."""
    aresponses.add(
        "wwlln.net", "/bad_endpoint", "get", aresponses.Response(text="", status=404)
    )

    with pytest.raises(RequestError):
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            await client.request("get", "http://wwlln.net/bad_endpoint")


@pytest.mark.asyncio
async def test_dump(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test that dumping the WWLLN data works."""
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.dump()

        assert len(data) == 5


@pytest.mark.asyncio
async def test_invalid_unit(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test raising a proper exception when an incorrect radius unit is used."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)

        with pytest.raises(ValueError):
            await client.within_radius(
                TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC, unit="random_unit"
            )


@pytest.mark.asyncio
async def test_nearest(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test retrieving the nearest strike."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        nearest_strike = await client.nearest(TEST_LATITUDE, TEST_LONGITUDE)

        assert nearest_strike == {
            "distance": 30.971194229766567,
            "lat": 56.13,
            "long": 92.73,
            "unixTime": 1561903959.4,
        }


@pytest.mark.asyncio
async def test_within_imperial(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test retrieving the nearest strikes within a mile radius."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_IMPERIAL, unit="imperial"
        )

        assert len(data) == 1
        assert data[0]["distance"] == 19.24482243239678


@pytest.mark.asyncio
async def test_within_metric(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test retrieving the nearest strikes within a kilometer radius."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC
        )

        assert len(data) == 1
        assert data[0]["distance"] == 30.971194229766567


@pytest.mark.asyncio
async def test_caching(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test that the caching mechanism works properly.

    Note that we have to bust the cache before executing this test since all tests use
    the same event loop."""
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)

        cache_exists = await cache.exists(DEFAULT_CACHE_KEY)
        assert not cache_exists

        await client.within_radius(TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC)

        cache_exists = await cache.exists(DEFAULT_CACHE_KEY)
        assert cache_exists


@pytest.mark.asyncio
async def test_invalid_cache_duration(caplog, event_loop):  # noqa
    """Test the cache duration floor."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        _ = Client(websession, cache_seconds=1)
        logs = [
            l
            for l in [
                "Setting cache timeout to lowest allowed" in e.message
                for e in caplog.records
            ]
            if l is not False
        ]
        assert len(logs) == 1


@pytest.mark.asyncio
async def test_invalid_json(aresponses, event_loop, fixture_dump_invalid_json):  # noqa
    """Test raising a proper exception when incorrect JSON is returned.

    Note that we have to bust the cache before executing this test since all tests use
    the same event loop."""
    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=fixture_dump_invalid_json, status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)

        with pytest.raises(RequestError):
            await client.within_radius(
                TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC
            )
