import pytest

pytestmark = [pytest.mark.django_db]


def test(api) -> None:
    got = api.get("/", as_response=True)

    assert got.status_code == 302
    assert got["Location"] == "/admin/"
