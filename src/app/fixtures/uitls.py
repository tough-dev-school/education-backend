import json
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def read_fixture():
    """JSON fixture reader"""

    def read_file(fixture):
        with open(f'{fixture}.json') as fp:
            return json.load(fp)

    return read_file


@pytest.fixture
def connect_mock_handler():
    def _connect_mock_handler(signal, **kwargs):
        handler = MagicMock()
        signal.connect(handler, **kwargs)
        return handler

    return _connect_mock_handler
