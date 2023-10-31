from decimal import Decimal
from typing import Any

import stripe

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank
from apps.stripebank.models import StripeNotification


class StripeBank(Bank):
    ue = 90  # ue stands for «условные единицы», this is some humour from 2000's
    currency = "EUR"
    currency_symbol = "€"
    acquiring_percent = Decimal(4)
    name = _("Stripe")

    def get_initial_payment_url(self) -> str:
        stripe.api_key = settings.STRIPE_API_KEY

        session = stripe.checkout.Session.create(
            line_items=self.get_items(),
            mode="payment",
            success_url=self.success_url,
            cancel_url=self.fail_url,
            customer_email=self.user.email,
            client_reference_id=self.order.slug,
        )

        return session.url

    def refund(self) -> None:
        stripe.api_key = settings.STRIPE_API_KEY

        latest_payment_notification = (
            StripeNotification.objects.filter(
                order=self.order,
                event_type="checkout.session.completed",
            ).order_by("-id")
        )[0]

        stripe.Refund.create(payment_intent=latest_payment_notification.payment_intent)

    def get_items(self) -> list[dict[str, Any]]:
        return [
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": self.order.item.name_international,
                    },
                    "unit_amount": self.price,
                },
                "quantity": 1,
            },
        ]
