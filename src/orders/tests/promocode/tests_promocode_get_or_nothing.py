import pytest

from orders.models import PromoCode

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize('name', [
    'TESTCODE',
    'testcode',
    'tEStCOde',
    '  TESTCODE',
    'TESTCODE  ',
])
def test_found(ten_percent_promocode, name):
    assert PromoCode.objects.get_or_nothing(name=name) == ten_percent_promocode


@pytest.mark.usefixtures('ten_percent_promocode')
def test_not_found():
    assert PromoCode.objects.get_or_nothing(name='NONEXISTANT') is None


def test_not_found_when_promo_code_is_disabled(ten_percent_promocode):
    ten_percent_promocode.setattr_and_save('active', False)

    assert PromoCode.objects.get_or_nothing(name='TESTCODE') is None


@pytest.mark.usefixtures('ten_percent_promocode')
def test_empty_name():
    assert PromoCode.objects.get_or_nothing(name=None) is None
