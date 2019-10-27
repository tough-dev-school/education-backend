import pytest
from app.test.api_client import DRFClient
from mixer.backend.django import mixer as _mixer


@pytest.fixture
def api():
    return DRFClient()


@pytest.fixture
def anon():
    return DRFClient(anon=True)


@pytest.fixture
def mixer():
    return _mixer
