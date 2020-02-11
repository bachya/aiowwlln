# ⚡️ aiowwlln: A simple Python3 wrapper for WWLLN

[![CI](https://github.com/bachya/aiowwlln/workflows/CI/badge.svg)](https://github.com/bachya/aiowwlln/actions)
[![PyPi](https://img.shields.io/pypi/v/aiowwlln.svg)](https://pypi.python.org/pypi/aiowwlln)
[![Version](https://img.shields.io/pypi/pyversions/aiowwlln.svg)](https://pypi.python.org/pypi/aiowwlln)
[![License](https://img.shields.io/pypi/l/aiowwlln.svg)](https://github.com/bachya/aiowwlln/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/bachya/aiowwlln/branch/dev/graph/badge.svg)](https://codecov.io/gh/bachya/aiowwlln)
[![Maintainability](https://api.codeclimate.com/v1/badges/e78f0ba106cbe14bfcea/maintainability)](https://codeclimate.com/github/bachya/aiowwlln/maintainability)
[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)

`aiowwlln` is a simple, `asyncio`-driven Python library for retrieving information on
lightning strikes from
[the World Wide Lightning Location Network (WWLLNN)](http://wwlln.net/).

**NOTE:** This library is built on an unofficial API; therefore, it may stop working at
any time.

# Installation

```python
pip install aiowwlln
```

# Python Versions

`aiowwlln` is currently supported on:

* Python 3.6
* Python 3.7
* Python 3.8

# Usage

`aiowwlln` starts within an
[aiohttp](https://aiohttp.readthedocs.io/en/stable/) `ClientSession`:

```python
import asyncio

from aiohttp import ClientSession

from aiowwlln import Client


async def main() -> None:
    """Create the aiohttp session and run the example."""
    async with ClientSession() as websession:
        # YOUR CODE HERE


asyncio.get_event_loop().run_until_complete(main())
```

Create a client, initialize it, then get to it:

```python
import asyncio
from datetime import datetime

from aiohttp import ClientSession

from aiowwlln import Client


async def main() -> None:
    """Create the aiohttp session and run the example."""
    async with ClientSession() as websession:
        client = aiowwlln.Client(websession)

        # Create a client and get all strike data – by default, data is cached for
        # 60 seconds (be a responsible data citizen!):
        client = Client(websession)
        await client.dump()

        # If you want to increase the cache to 24 hours, go for it:
        client = Client(websession, cache_seconds=60*60*24)
        await client.dump()

        # Get strike data within a 50 km radius around a set of coordinates (note that
        # the cache still applies):
        await client.within_radius(
            56.1621538, 92.2333561, 50, unit="metric"
        )

        # Get strike data within a 10 mile radius around a set of coordinates (note that
        # the cache still applies):
        await client.within_radius(
            56.1621538, 92.2333561, 10, unit="imperial"
        )

        # Get strike data within a 50 km radius around a set of coordinates _and_
        # within the last 10 minutes:
        await client.within_radius(
            56.1621538, 92.2333561, 50, unit="metric", window=timedelta(minutes=10)
        )


asyncio.get_event_loop().run_until_complete(main())
```

# Contributing

1. [Check for open features/bugs](https://github.com/bachya/aiowwlln/issues)
  or [initiate a discussion on one](https://github.com/bachya/aiowwlln/issues/new).
2. [Fork the repository](https://github.com/bachya/aiowwlln/fork).
3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`
4. (_optional, but highly recommended_) Enter the virtual environment: `source ./venv/bin/activate`
5. Install the dev environment: `script/setup`
6. Code your new feature or bug fix.
7. Write tests that cover your new functionality.
8. Run tests and ensure 100% code coverage: `script/test`
9. Update `README.md` with any new documentation.
10. Add yourself to `AUTHORS.md`.
11. Submit a pull request!

