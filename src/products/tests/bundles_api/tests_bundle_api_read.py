import pytest

pytestmark = [
    pytest.mark.django_db,
]


def test_retrieve(api, bundle):
    got = api.get("/api/v2/bundles/pinetree-tickets/")

    assert got["name"] == "Флаг и билет на ёлку"
