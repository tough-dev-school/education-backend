import pytest

from core.test.factory import FixtureFactory
from core.test.mixer import mixer as _mixer


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def factory():
    return FixtureFactory()
