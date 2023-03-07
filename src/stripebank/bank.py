from decimal import Decimal
from typing import Any

import stripe

from django.conf import settings

from banking.base import Bank


class StripeBank(Bank):
    ue = 80  # ue stands for «условные единицы», this is some humour from 2000's
    currency = "EUR"
    currency_symbol = "€"
    acquiring_percent = Decimal(4)
    name = "Страйп"

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
