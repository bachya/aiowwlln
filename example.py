"""Run an example script to quickly test."""
import asyncio

from aiohttp import ClientSession

from aiowwlln import Client
from aiowwlln.errors import WWLLNError

TARGET_LATITUDE = 56.1621538
TARGET_LONGITUDE = 92.2333561
TARGET_RADIUS_KM = 50


async def main() -> None:
    """Create the aiohttp session and run the example."""
    async with ClientSession() as websession:
        try:
            # Create a client:
            client = Client(websession)

            # Get all strike data:
            print(await client.dump())

            # Get strike data within a radius around a set of coordinates:
            print(
                await client.within_radius(
                    TARGET_LATITUDE, TARGET_LONGITUDE, TARGET_RADIUS_KM
                )
            )

            # Get the nearest strike to a set of coordinates:
            print(await client.nearest(TARGET_LATITUDE, TARGET_LONGITUDE))

        except WWLLNError as err:
            print(err)


asyncio.get_event_loop().run_until_complete(main())
