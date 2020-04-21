"""Run an example script to quickly test."""
import asyncio
from datetime import timedelta

from aiohttp import ClientSession

from aiowwlln import Client
from aiowwlln.errors import WWLLNError

TARGET_LATITUDE = 56.1621538
TARGET_LONGITUDE = 92.2333561
TARGET_RADIUS_KM = 50


async def main() -> None:
    """Create the aiohttp session and run the example."""
    async with ClientSession() as session:
        try:
            # Create a client:
            client = Client(session=session)

            # Get all strike data:
            print(await client.dump())

            # Get strike data within a 50km radius around a set of coordinates _and_
            # within the last hour:
            print(
                await client.within_radius(
                    TARGET_LATITUDE,
                    TARGET_LONGITUDE,
                    TARGET_RADIUS_KM,
                    window=timedelta(hours=1),
                )
            )
        except WWLLNError as err:
            print(err)


asyncio.run(main())
