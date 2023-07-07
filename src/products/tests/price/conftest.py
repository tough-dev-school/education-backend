import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def record(factory):
    return factory.record(slug="home-video", price="100500.00", old_price="100500.95")
