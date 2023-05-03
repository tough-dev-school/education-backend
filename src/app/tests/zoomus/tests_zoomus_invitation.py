import pytest

from app.integrations.zoomus import ZoomusHTTPException

pytestmark = [pytest.mark.django_db]


INVITE_URL = "https://api.zoom.us/v2/webinars/100500/registrants/"

SUCCESS_JSON = {
    "id": "0022304902349",
    "join_url": "https://join.url",
    "registrant_id": "CBjmE6twOzqzweby",
    "start_time": "2020-04-30T17:00:00Z",
    "topic": "Тестовый вебинар",
}


def test_ok(client, user):
    def assertions(request, context):
        req = request.json()
        assert req["first_name"] == "Авраам"
        assert req["last_name"] == "Пейзенгольц"
        assert req["email"] == "abrakham@mail.ru"

        assert "Bearer" in request.headers["Authorization"]

        return SUCCESS_JSON

    client.http_mock.post(INVITE_URL, json=assertions, status_code=201)

    client.invite(100500, user)


def test_fail(client, user):
    client.http_mock.post(INVITE_URL, json={}, status_code=400)

    with pytest.raises(ZoomusHTTPException):
        client.invite(100500, user)
