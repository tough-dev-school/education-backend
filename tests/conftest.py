import pytest

from django.core.cache import cache

pytest_plugins = [
    "app.factory",
    "app.fixtures",
    "users.fixtures",
    "apps.orders.factory",
    "apps.diplomas.factory",
    "apps.products.factory",
    "apps.products.fixtures",
]


@pytest.fixture(autouse=True)
def _cache(request):
    """Clear django cache after each test run."""
    yield
    cache.clear()
