"""Define various geo utility functions."""
from math import radians, cos, sin, asin, sqrt

AVG_EARTH_RADIUS_METRIC = 6371
AVG_EARTH_RADIUS_IMPERIAL = 3958.8


def get_nearest_by_coordinates(
    data: list,
    latitude_key: str,
    longitude_key: str,
    target_latitude: float,
    target_longitude: float,
) -> dict:
    """Get the closest dict entry based on latitude/longitude."""
    return min(
        data,
        key=lambda s: haversine(
            target_latitude, target_longitude, s[latitude_key], s[longitude_key]
        ),
    )


def haversine(
    lat1: float, lon1: float, lat2: float, lon2: float, *, unit: str = "metric"
) -> float:
    """Determine the distance between two latitude/longitude pairs."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    calc_a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    calc_c = 2 * asin(sqrt(calc_a))

    if unit == "metric":
        return AVG_EARTH_RADIUS_METRIC * calc_c
    return AVG_EARTH_RADIUS_IMPERIAL * calc_c
