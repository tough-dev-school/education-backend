import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(price="500", old_price="500.95")


def test_retrieve(api, course):
    got = api.get(f"/api/v2/courses/{course.slug}/")

    assert got["price"] == "500"
    assert got["old_price"] == "500,95"
    assert got["formatted_price"] == "5̶0̶0̶,̶9̶5̶ 500 ₽"
