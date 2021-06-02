import pytest

from app.test.factory import FixtureFactory
from app.test.mixer import mixer as _mixer


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def factory():
    return FixtureFactory()
