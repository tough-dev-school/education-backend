import pytest
from django.core.cache import cache
from django.utils import translation

# fmt: off
pytest_plugins = [
    "apps.diplomas.factory",
    "apps.orders.factory",
    "apps.b2b.factory",
    "apps.products.factory",
    "apps.banking.factory",
    "core.factory",

    "apps.products.fixtures",
    "apps.users.fixtures",
    "apps.lms.factory",
    "core.fixtures",
]
# fmt: on


@pytest.fixture(autouse=True)
def _cache() -> None:  # type: ignore
    """Clear django cache after each test run."""
    yield
    cache.clear()


@pytest.fixture
def _en() -> None: # type: ignore
    """Disable django translation"""
    with translation.override('en'):
        yield
