import json
from unittest.mock import MagicMock

import pytest
from mixer.backend.django import mixer as _mixer

from app.test.api_client import DRFClient


@pytest.fixture
def api():
    return DRFClient()


@pytest.fixture
def anon():
    return DRFClient(anon=True)


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User')


@pytest.fixture
def read_fixture():
    """JSON fixture reader"""

    def read_file(f):
        with open(f'{f}.json') as fp:
            return json.load(fp)

    return read_file


@pytest.fixture
def connect_mock_handler():
    def _connect_mock_handler(signal, **kwargs):
        handler = MagicMock()
        signal.connect(handler, **kwargs)
        return handler

    return _connect_mock_handler
