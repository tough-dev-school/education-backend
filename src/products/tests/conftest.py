import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def testcode(mixer):
    return mixer.blend('orders.PromoCode', name='TESTCODE', discount_percent=10)
