import pytest
from contextlib import nullcontext as does_not_raise

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_stripe_refund(mocker):
    return mocker.patch("stripe.Refund.create")

def test_refund(stripe, stripe_notification_checkout_completed, mock_stripe_refund):
    stripe.refund()

    mock_stripe_refund.assert_called_once_with(payment_intent=stripe_notification_checkout_completed.payment_intent)


def test_not_fail_if_last_notification_not_linked_with_order(stripe, stripe_notification_checkout_completed, mixer, mock_stripe_refund):
    mixer.blend(
        "stripebank.StripeNotification",
        id=99999,
        order=None,  # the latest notification of unknown type and not linked with order
        amount=0,
    )

    stripe.refund()

    mock_stripe_refund.assert_called_once_with(payment_intent=stripe_notification_checkout_completed.payment_intent)
