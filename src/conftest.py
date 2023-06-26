import pytest
from typing import Generator

from django.core.cache import cache

pytest_plugins = [
    "app.factory",
    "app.fixtures",
    "users.fixtures",
    "orders.factory",
    "diplomas.factory",
]


@pytest.fixture(autouse=True)
def _cache(request: pytest.FixtureRequest) -> Generator:
    """Clear django cache after each test run."""
    yield
    cache.clear()
