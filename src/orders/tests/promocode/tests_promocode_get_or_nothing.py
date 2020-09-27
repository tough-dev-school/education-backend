import pytest

from orders.models import PromoCode

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def promocode(mixer):
    return mixer.blend('orders.PromoCode', name='TESTCODE')


def test_found(promocode):
    assert PromoCode.objects.get_or_nothing('TESTCODE') == promocode


def test_not_found(promocode):
    assert PromoCode.objects.get_or_nothing('NONEXISTANT') is None
