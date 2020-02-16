"""Define tests for the client object."""
from datetime import timedelta
import json

from aiocache import SimpleMemoryCache
import aiohttp
import pytest

from aiowwlln import Client
from aiowwlln.client import DEFAULT_CACHE_KEY
from aiowwlln.errors import RequestError

from .common import (
    TEST_LATITUDE,
    TEST_LONGITUDE,
    TEST_RADIUS_IMPERIAL,
    TEST_RADIUS_METRIC,
)


@pytest.mark.asyncio
async def test_bad_request(aresponses):
    """Test that the proper exception is raised during a recurring bad request."""
    aresponses.add(
        "wwlln.net", "/bad_endpoint", "get", aresponses.Response(text="", status=404)
    )
    aresponses.add(
        "wwlln.net", "/bad_endpoint", "get", aresponses.Response(text="", status=404)
    )

    with pytest.raises(RequestError):
        async with aiohttp.ClientSession() as websession:
            client = Client(websession)
            await client.request("get", "http://wwlln.net/bad_endpoint")


@pytest.mark.asyncio
async def test_dump(aresponses, dump_response):
    """Test that dumping the WWLLN data works."""
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(dump_response), status=200),
    )

    async with aiohttp.ClientSession() as websession:
        client = Client(websession)
        data = await client.dump()
        assert len(data) == 6


@pytest.mark.asyncio
async def test_invalid_unit():
    """Test raising a proper exception when an incorrect radius unit is used."""
    async with aiohttp.ClientSession() as websession:
        client = Client(websession)

        with pytest.raises(ValueError):
            await client.within_radius(
                TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC, unit="random_unit"
            )


@pytest.mark.asyncio
async def test_within_imperial():
    """Test retrieving the nearest strikes within a mile radius."""
    async with aiohttp.ClientSession() as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_IMPERIAL, unit="imperial"
        )
        assert len(data) == 2

        first_strike = next(iter(data.values()))
        assert first_strike["distance"] == 19.24482243239678


@pytest.mark.asyncio
async def test_within_metric():
    """Test retrieving the nearest strikes within a kilometer radius."""
    async with aiohttp.ClientSession() as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC
        )
        assert len(data) == 2

        first_strike = next(iter(data.values()))
        assert first_strike["distance"] == 30.971194229766567


@pytest.mark.asyncio
async def test_within_window(aresponses, dump_response):
    """Test retrieving the nearest strikes within a 10-minute window."""
    # Bust the cache since we're parametrizing the input data:
    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(dump_response), status=200),
    )

    async with aiohttp.ClientSession() as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE,
            TEST_LONGITUDE,
            TEST_RADIUS_METRIC,
            window=timedelta(minutes=10),
        )
        assert len(data) == 1


@pytest.mark.asyncio
async def test_caching(aresponses, dump_response):
    """Test that the caching mechanism works properly.

    Note that we have to bust the cache before executing this test since all tests use
    the same event loop.
    """
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(dump_response), status=200),
    )

    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    async with aiohttp.ClientSession() as websession:
        client = Client(websession)

        cache_exists = await cache.exists(DEFAULT_CACHE_KEY)
        assert not cache_exists

        await client.within_radius(TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC)

        cache_exists = await cache.exists(DEFAULT_CACHE_KEY)
        assert cache_exists


@pytest.mark.asyncio
async def test_invalid_cache_duration(caplog):
    """Test the cache duration floor."""
    async with aiohttp.ClientSession() as websession:
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
async def test_invalid_json_retry_failure(aresponses):
    """Test a failed retry after getting a failed JSON error.

    Note that we have to bust the cache before executing this test since all tests use
    the same event loop.
    """
    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text="This isn't JSON", status=200),
    )
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text="This isn't JSON", status=200),
    )

    with pytest.raises(RequestError):
        async with aiohttp.ClientSession() as websession:
            client = Client(websession)
            await client.dump()


@pytest.mark.asyncio
async def test_invalid_json_retry_successful(aresponses, dump_response):
    """Test a successful retry after getting a failed JSON error.

    Note that we have to bust the cache before executing this test since all tests use
    the same event loop.
    """
    cache = SimpleMemoryCache()
    await cache.delete(DEFAULT_CACHE_KEY)

    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text="This isn't JSON", status=200),
    )
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(dump_response), status=200),
    )

    async with aiohttp.ClientSession() as websession:
        client = Client(websession)
        data = await client.dump()
        assert len(data) == 6
