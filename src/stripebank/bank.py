from typing import Any

import stripe
from django.conf import settings

from banking.base import Bank


class StripeBank(Bank):
    ue = 105  # ue stends for «условные единицы», this is some humour from 2000's

    def get_initial_payment_url(self) -> str:
        stripe.api_key = settings.STRIPE_API_KEY

        session = stripe.checkout.Session.create(
            line_items=self.get_items(),
            mode='payment',
            success_url=self.success_url,
            cancel_url=self.fail_url,
            customer_email=self.user.email,
            client_reference_id=f'tds-{self.order.id}',
        )

        return session.url

    def get_items(self) -> list[dict[str, Any]]:
        return [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': self.order.item.name_international,
                    },
                    'unit_amount': self.price,
                },
                'quantity': 1,
            },
        ]
