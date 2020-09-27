import pytest

from orders.models import PromoCode

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def promocode(mixer):
    return mixer.blend('orders.PromoCode', name='TESTCODE')


@pytest.mark.parametrize('name', [
    'TESTCODE',
    'testcode',
    'tEStCOde',
])
def test_found(promocode, name):
    assert PromoCode.objects.get_or_nothing(name=name) == promocode


def test_not_found():
    assert PromoCode.objects.get_or_nothing(name='NONEXISTANT') is None


def test_not_found_when_promo_code_is_disabled(promocode):
    promocode.setattr_and_save('active', False)

    assert PromoCode.objects.get_or_nothing(name='TESTCODE') is None
