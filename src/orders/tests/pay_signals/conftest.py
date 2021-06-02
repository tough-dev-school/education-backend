import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory):
    return factory.order()
