import json
import pytest


@pytest.fixture
def read_fixture():
    """JSON fixture reader"""

    def read_file(fixture):
        with open(f'{fixture}.json') as fp:
            return json.load(fp)

    return read_file
