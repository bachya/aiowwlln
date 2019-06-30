"""Define tests for the client object."""
# pylint: disable=redefined-outer-name,unused-import
import json

import aiohttp
import pytest

from aiowwlln import Client
from aiowwlln.errors import RequestError

from .const import (
    TEST_LATITUDE,
    TEST_LONGITUDE,
    TEST_RADIUS_IMPERIAL,
    TEST_RADIUS_METRIC,
)
from .fixtures.client import fixture_dump_json  # noqa


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
    """Test raising a proper except when an incorrect radius unit is used."""
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)

        with pytest.raises(ValueError):
            await client.within_radius(
                TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC, unit="random_unit"
            )


@pytest.mark.asyncio
async def test_nearest(aresponses, event_loop, fixture_dump_json):  # noqa
    """Test retrieving the nearest strike."""
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

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
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

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
    aresponses.add(
        "wwlln.net",
        "/new/map/data/current.json",
        "get",
        aresponses.Response(text=json.dumps(fixture_dump_json), status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:
        client = Client(websession)
        data = await client.within_radius(
            TEST_LATITUDE, TEST_LONGITUDE, TEST_RADIUS_METRIC
        )

        assert len(data) == 1
        assert data[0]["distance"] == 30.971194229766567
