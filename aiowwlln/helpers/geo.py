"""Define various geo utility functions."""
from math import asin, cos, radians, sin, sqrt

AVG_EARTH_RADIUS_METRIC: int = 6371
AVG_EARTH_RADIUS_IMPERIAL: float = 3958.8


def haversine(
    lat1: float, lon1: float, lat2: float, lon2: float, *, unit: str = "metric"
) -> float:
    """Determine the distance between two latitude/longitude pairs."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon: float = lon2 - lon1
    dlat: float = lat2 - lat1
    calc_a: float = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    calc_c: float = 2 * asin(sqrt(calc_a))

    if unit == "metric":
        return AVG_EARTH_RADIUS_METRIC * calc_c
    return AVG_EARTH_RADIUS_IMPERIAL * calc_c
