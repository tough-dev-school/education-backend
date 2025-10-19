import pytest
from django.core.cache import cache
from django.utils import translation

pytest_plugins = [
    "apps.diplomas.factory",
    "apps.orders.factory",
    "apps.b2b.factory",
    "apps.products.factory",
    "apps.banking.factory",
    "core.factory",
    "apps.products.fixtures",
    "apps.banking.fixtures",
    "apps.users.fixtures",
    "apps.lms.factory",
    "apps.homework.factory",
    "apps.dashamail.fixtures",
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
