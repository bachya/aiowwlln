"""Define fixtures for the client."""
import pytest


@pytest.fixture()
def fixture_dump_json():
    """Return an unfiltered strike data response."""
    return {
        "1252081": {"unixTime": 1561903959.4, "lat": 19.64, "long": -82.93},
        "1830720": {"unixTime": 1561903959.5, "lat": 37, "long": -67.7},
        "4996442": {"unixTime": 1561903959, "lat": 37.59, "long": -66.58},
        "5743673": {"unixTime": 1561903959.4, "lat": 56.13, "long": 92.73},
        "9841561": {"unixTime": 1561903959.5, "lat": 36.99, "long": -67.72},
    }


@pytest.fixture()
def fixture_dump_invalid_json():
    """Return an invalid JSON response."""
    return (
        '{ "1252081": {"unixTime": 1561903959.4, "lat": 19.64, "long": -82.93}, '
        '"1830720": {"unixTime": 1561903959.5, "lat": 37, "long": -67.7}, "4996442":'
        ' {"unixTime": 1561903959, "lat": 37.59, "long": -66.58}, "5743673": '
        '{"unixTime": 1561903959.4, "lat": 56.13, "long": 92.73} "9841561": '
        '{"unixTime": 1561903959.5, "lat": 36.99, "long": -67.72} }'
    )
