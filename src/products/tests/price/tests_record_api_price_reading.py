import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(factory):
    return factory.record(price="500", old_price="500.95")


def test_retrieve(api, record):
    got = api.get(f"/api/v2/records/{record.slug}/")

    assert got["price"] == "500"
    assert got["old_price"] == "500,95"
    assert got["formatted_price"] == "5̶0̶0̶,̶9̶5̶ 500 ₽"
