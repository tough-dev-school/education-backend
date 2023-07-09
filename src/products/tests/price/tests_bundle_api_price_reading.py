import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def bundle(factory):
    return factory.bundle(slug="pinetree-tickets", name="Флаг и билет на ёлку", price="500", old_price="500.95")


def test_retrieve(api, bundle):
    got = api.get(f"/api/v2/bundles/{bundle.slug}/")

    assert got["price"] == "500"
    assert got["old_price"] == "500,95"
    assert got["formatted_price"] == "5̶0̶0̶,̶9̶5̶ 500 ₽"
