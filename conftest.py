import pytest
from django.core.cache import cache

# fmt: off
pytest_plugins = [
    "apps.diplomas.factory",
    "apps.orders.factory",
    "apps.products.factory",
    "core.factory",

    "apps.products.fixtures",
    "apps.users.fixtures",
    "core.fixtures",
]
# fmt: on


@pytest.fixture(autouse=True)
def _cache():
    """Clear django cache after each test run."""
    yield
    cache.clear()
