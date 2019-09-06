"""Define tests for the client object."""
# pylint: disable=redefined-outer-name,unused-import
from datetime import timedelta
import json
import time

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
async def test_invalid_unit(event_loop):  # noqa
    """Test raising a proper exception when an incorrect radius unit is used."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)

        with pytest.raises(ValueError):
            await client.within_radius(
                TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC, unit="random_unit"
            )


@pytest.mark.asyncio
async def test_within_imperial(event_loop):  # noqa
    """Test retrieving the nearest strikes within a mile radius."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_IMPERIAL, unit="imperial"
        )

        assert len(data) == 1

        first_strike = next(iter(data.values()))
        assert first_strike["distance"] == 19.24482243239678


@pytest.mark.asyncio
async def test_within_metric(event_loop):  # noqa
    """Test retrieving the nearest strikes within a kilometer radius."""
    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC
        )

        assert len(data) == 1

        first_strike = next(iter(data.values()))
        assert first_strike["distance"] == 30.971194229766567


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fixture_dump_json",
    [{"999999": {"unixTime": time.time(), "lat": 56.13, "long": 92.73}}],
)
async def test_within_window(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test retrieving the nearest strikes within a 10-minute window."""
    # Bust the cache since we're parametrizing the input data:
    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE,
            TEST_LONGITUDE,
            TEST_RADIUS_METRIC,
            window=timedelta(minutes=10),
        )

        assert len(data) == 1


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
async def test_invalid_json_retry_failure(
    aresponses, event_loop, fixture_dump_invalid_json  # noqa
):
    """Test a failed retry after getting a failed JSON error.

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
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=fixture_dump_invalid_json, status=200),
    )

    with pytest.raises(RequestError):
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            await client.dump()


@pytest.mark.asyncio
async def test_invalid_json_retry_successful(
    aresponses, event_loop, fixture_dump_invalid_json, fixture_dump_json  # noqa
):
    """Test a successful retry after getting a failed JSON error.

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
