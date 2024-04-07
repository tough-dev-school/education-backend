import pytest

pytestmark = [pytest.mark.django_db]


def test_schema(api):
    got = api.get("/api/v2/docs/schema/", as_response=True)

    assert got.status_code == 200
    assert got["Content-type"] == "application/vnd.oai.openapi; charset=utf-8"


def test_swagger(api):
    got = api.get("/api/v2/docs/swagger/", as_response=True)

    assert got.status_code == 200
    assert got["Content-type"] == "text/html; charset=utf-8"
