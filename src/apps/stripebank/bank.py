from decimal import Decimal
from typing import Any

import stripe
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank
from apps.stripebank.models import StripeNotification


class BaseStripeBank(Bank):
    currency = "USD"
    acquiring_percent = Decimal(4)
    name = _("Stripe")
    api_key: str = ""
    webhook_secret: str = ""

    @property
    def is_partial_refund_available(self) -> bool:
        return True

    def get_initial_payment_url(self) -> str:
        stripe.api_key = self.api_key

        session = stripe.checkout.Session.create(
            line_items=self.get_items(),
            mode="payment",
            success_url=self.success_url,
            cancel_url=self.fail_url,
            customer_email=self.user.email,
            client_reference_id=self.order.slug,
        )

        return session.url

    def refund(self, amount: Decimal | None = None) -> None:
        stripe.api_key = self.api_key

        latest_payment_notification = (
            StripeNotification.objects.filter(
                order=self.order,
                event_type="checkout.session.completed",
            ).order_by("-id")
        )[0]

        refund_amount_data = {"amount": self.get_formatted_amount(amount)} if amount else {}
        stripe.Refund.create(payment_intent=latest_payment_notification.payment_intent, **refund_amount_data)  # type: ignore

    def get_items(self) -> list[dict[str, Any]]:
        return [
            {
                "price_data": {
                    "currency": self.currency.lower(),
                    "product_data": {
                        "name": self.order.item.name_international,
                    },
                    "unit_amount": self.price,
                },
                "quantity": 1,
            },
        ]


class StripeBankUSD(BaseStripeBank):
    ue = Decimal(80)
    currency = "USD"
    currency_symbol = "$"
    name = _("Stripe USD")
    api_key = settings.STRIPE_USD_API_KEY
    webhook_secret = settings.STRIPE_USD_WEBHOOK_SECRET


class StripeBankKZT(BaseStripeBank):
    ue = Decimal("0.18")
    currency = "KZT"
    currency_symbol = "₸"
    name = _("Stripe KZT")
    api_key = settings.STRIPE_KZT_API_KEY
    webhook_secret = settings.STRIPE_KZT_WEBHOOK_SECRET
