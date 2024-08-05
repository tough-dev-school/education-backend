import json

import pytest

from apps.stripebank.bank import StripeBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def stripe(order):
    return StripeBank(order)


@pytest.fixture(autouse=True)
def _set_stripe_key(settings):
    settings.STRIPE_API_KEY = "sk_test_100500"


@pytest.fixture(autouse=True)
def _fix_stripe_course(mocker):
    mocker.patch("apps.stripebank.bank.StripeBank.ue", 70)  # let it be forever :'(


@pytest.fixture
def course(factory):
    return factory.course(name="Курс кройки и шитья", name_international="Cutting and Sewing")


@pytest.fixture
def order(course, factory):
    return factory.order(item=course, price=100500, is_paid=False)


@pytest.fixture
def load_stipe_webhook():
    def load_filename(webhook_filename: str):
        with open(f"apps/stripebank/tests/stripebank/.fixtures/{webhook_filename}", "r") as fp:
            return json.load(fp)

    return load_filename


@pytest.fixture
def _disable_signature_verification(mocker):
    mocker.patch("stripe.WebhookSignature.verify_header", return_value=True)


@pytest.fixture
def webhook_checkout_session_completed(load_stipe_webhook, order):
    webhook_data = load_stipe_webhook("webhook_checkout_session_completed.json")
    webhook_data["data"]["object"]["client_reference_id"] = order.slug
    return webhook_data


@pytest.fixture
def webhook_charge_refunded(load_stipe_webhook):
    return load_stipe_webhook("webhook_charge_refunded.json")


@pytest.fixture
def stripe_notification_checkout_completed(order, mixer):
    return mixer.blend(
        "stripebank.StripeNotification",
        order=order,
        event_type="checkout.session.completed",
        payment_intent="pi_3O42fCHFzM1bXe8Q0EbUXgsQ",
        amount=50,
    )
