import json
import pytest

from stripebank.bank import StripeBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def stripe(order):
    return StripeBank(order)


@pytest.fixture(autouse=True)
def _set_stripe_key(settings):
    settings.STRIPE_API_KEY = "sk_test_100500"


@pytest.fixture(autouse=True)
def _fix_stripe_course(mocker):
    mocker.patch("stripebank.bank.StripeBank.ue", 70)  # let it be forever :'(


@pytest.fixture
def course(factory):
    return factory.course(name="Курс кройки и шитья", name_international="Cutting and Sewing")


@pytest.fixture
def order(course, factory):
    return factory.order(item=course, price=100500, is_paid=False)


@pytest.fixture
def webhook(order):
    with open("./stripebank/tests/.fixtures/webhook.json", "r") as fp:
        webhook = json.load(fp)
        webhook["data"]["object"]["client_reference_id"] = order.slug

        return webhook
