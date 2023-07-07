import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory, bundle):
    return factory.order(item=bundle)
