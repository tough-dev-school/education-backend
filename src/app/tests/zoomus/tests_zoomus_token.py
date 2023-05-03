import pytest

import jwt

from app.integrations.zoomus.http import ZoomusClientHTTP

pytestmark = [
    pytest.mark.freeze_time("2032-12-01 15:30"),
]


def test():
    client = ZoomusClientHTTP(
        base_url="https://test.com",
        api_key="test",
        api_secret="g0d",
    )

    decoded = jwt.decode(client.token, key="g0d", algorithms=["HS256"])

    assert decoded["iss"] == "test"
    assert decoded["exp"] == 1985545800
