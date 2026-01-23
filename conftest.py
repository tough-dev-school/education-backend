import pytest
from django.core.cache import cache
from django.utils import translation

pytest_plugins = [
    "apps.b2b.factory",
    "apps.banking.factory",
    "apps.banking.fixtures",
    "apps.dashamail.fixtures",
    "apps.diplomas.factory",
    "apps.homework.factory",
    "apps.lms.factory",
    "apps.orders.factory",
    "apps.orders.fixtures",
    "apps.products.factory",
    "apps.products.fixtures",
    "apps.users.factory",
    "apps.users.fixtures",
    "core.factory",
    "core.fixtures",
]


@pytest.fixture(autouse=True)
def _cache() -> None:
    """Clear django cache after each test run."""
    yield
    cache.clear()


@pytest.fixture
def _en() -> None:
    """Disable django translation"""
    with translation.override("en"):
        yield
