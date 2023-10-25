import pytest

pytestmark = [
    pytest.mark.django_db,
]


def test_refund(stripe, stripe_notification_checkout_completed, order, mocker):
    mock_refund = mocker.patch("stripe.Refund.create")

    stripe.refund()

    mock_refund.assert_called_once_with(payment_intent=stripe_notification_checkout_completed.payment_intent)
