"""Define common test utilities."""
import os

TEST_LATITUDE = 56.1621538
TEST_LONGITUDE = 92.2333561
TEST_RADIUS_IMPERIAL = 80
TEST_RADIUS_METRIC = 50


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()
