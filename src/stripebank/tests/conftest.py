import pytest

from stripebank.bank import StripeBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def stripe(order):
    return StripeBank(order)


@pytest.fixture(autouse=True)
def _set_stripe_key(settings):
    settings.STRIPE_API_KEY = 'sk_test_100500'


@pytest.fixture(autouse=True)
def _fix_stripe_course(mocker):
    mocker.patch('stripebank.bank.UE', 70)  # let it be forever :'(


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', name='Курс кройки и шитья', price=100500, name_international='Cutting and Sewing')


@pytest.fixture
def order(course, factory):
    return factory.order(item=course, is_paid=False)
