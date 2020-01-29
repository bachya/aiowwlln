"""Define fixtures, constants, etc. available for all tests."""
from time import time

import pytest


@pytest.fixture()
def dump_response():
    """Return a strike payload with at least one current strike."""
    return {
        "1252081": {"unixTime": 1561903959.4, "lat": 19.64, "long": -82.93},
        "1830720": {"unixTime": 1561903959.5, "lat": 37, "long": -67.7},
        "4996442": {"unixTime": 1561903959, "lat": 37.59, "long": -66.58},
        "5743673": {"unixTime": 1561903959.4, "lat": 56.13, "long": 92.73},
        "9841561": {"unixTime": 1561903959.4, "lat": 36.99, "long": -67.72},
        "999999": {"unixTime": time(), "lat": 56.13, "long": 92.73},
    }
