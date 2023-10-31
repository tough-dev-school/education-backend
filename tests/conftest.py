import pytest

from django.core.cache import cache

# fmt: off
pytest_plugins = [
    "tests.factories.apps.diplomas",
    "tests.factories.apps.orders",
    "tests.factories.apps.products",
    "tests.factories.apps.studying",
    "tests.factories.apps.users",
    "tests.factories.core",

    "tests.fixtures.apps.products",
    "tests.fixtures.apps.users",
    "tests.fixtures.core",
]
# fmt: on


@pytest.fixture(autouse=True)
def _cache(request):
    """Clear django cache after each test run."""
    yield
    cache.clear()
