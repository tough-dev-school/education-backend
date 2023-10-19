import pytest

from django.core.cache import cache

pytest_plugins = [
    "apps.diplomas.factory",
    "apps.orders.factory",
    "apps.products.factory",
    "apps.products.fixtures",
    "apps.users.fixtures",
    "core.factory",
    "core.fixtures",
]


@pytest.fixture(autouse=True)
def _cache(request):
    """Clear django cache after each test run."""
    yield
    cache.clear()
