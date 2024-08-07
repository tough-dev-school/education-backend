import json
from datetime import datetime, timezone

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30Z"),
]


@pytest.fixture
def order(factory):
    return factory.order(bank_id="stripe")


@pytest.fixture
def webhook_checkout_completed(order):
    with open("apps/stripebank/tests/stripebank/.fixtures/webhook_checkout_session_completed.json", "r") as fp:
        bank_data = json.load(fp)
        bank_data["data"]["object"]["client_reference_id"] = order.slug

        return bank_data


@pytest.fixture(autouse=True)
def _disable_signature_verification(mocker):
    mocker.patch("stripe.WebhookSignature.verify_header", return_value=True)


def test(anon, webhook_checkout_completed, order):
    anon.post("/api/v2/banking/stripe-webhooks/", webhook_checkout_completed, expected_status_code=200)

    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)


@pytest.mark.parametrize("webhook_event_type", ["checkout.session.expired", "f4ke"])
def test_wrong_status(anon, order, webhook_checkout_completed, webhook_event_type):
    webhook_checkout_completed["type"] = webhook_event_type

    anon.post("/api/v2/banking/stripe-webhooks/", webhook_checkout_completed, expected_status_code=200)

    order.refresh_from_db()
    assert order.paid is None
