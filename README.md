# ⚡️ aiowwlln: A simple Python3 wrapper for WWLLN

[![Travis CI](https://travis-ci.org/bachya/aiowwlln.svg?branch=master)](https://travis-ci.org/bachya/aiowwlln)
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

* Python 3.5
* Python 3.6
* Python 3.7

However, running the test suite currently requires Python 3.6 or higher; tests
run on Python 3.5 will fail.

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

from aiohttp import ClientSession

from aiowwlln import Client


async def main() -> None:
    """Create the aiohttp session and run the example."""
    async with ClientSession() as websession:
        client = aiowwlln.Client(websession)

        # Create a client:
        client = Client(websession)

        # Get all strike data:
        await client.dump()

        # Get strike data within a 50 km radius around a set of coordinates:
        await client.within_radius(
            56.1621538, 92.2333561, 50, unit="metric"
        )

        # Get strike data within a 10 mile radius around a set of coordinates:
        await client.within_radius(
            56.1621538, 92.2333561, 10, unit="imperial"
        )

        # Get the nearest strike to a set of coordinates:
        await client.nearest(56.1621538, 92.2333561)


asyncio.get_event_loop().run_until_complete(main())
```

# Contributing

1. [Check for open features/bugs](https://github.com/bachya/aiowwlln/issues)
  or [initiate a discussion on one](https://github.com/bachya/aiowwlln/issues/new).
2. [Fork the repository](https://github.com/bachya/aiowwlln/fork).
3. Install the dev environment: `make init`.
4. Enter the virtual environment: `pipenv shell`
5. Code your new feature or bug fix.
6. Write a test that covers your new functionality.
7. Run tests and ensure 100% code coverage: `make coverage`
8. Add yourself to `AUTHORS.md`.
9. Submit a pull request!
