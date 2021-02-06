import requests
from django.conf import settings

from app.banking import Bank


class TinkoffCreditRequestException(Exception):
    pass


class TinkoffCredit(Bank):
    def get_initial_payment_url(self) -> str:
        result = self.call(
            url=self.get_create_order_url(),
            payload={
                'shopId': settings.TINKOFF_CREDIT_SHOP_ID,
                'showcaseId': settings.TINKOFF_CREDIT_SHOWCASE_ID,
                'sum': self.price,
                'orderNumber': self.order.id,
                'promoCode': self.order.item.tinkoff_credit_promo_code or None,
                'values': self.get_user(),
                'items': self.get_items(),
            },
        )

        return result['link']

    def call(self, url: str, payload: dict) -> dict:
        """Query TinkoffCredit API
        """
        r = requests.post(url, json=payload)

        if r.status_code != 200:
            errors = r.json()['errors']
            raise TinkoffCreditRequestException(f'Incorrect HTTP-status code for {url}: {r.status_code}, {errors}')

        return r.json()

    def get_items(self):
        return [{
            'name': self.order.item.name_receipt,
            'price': self.price,  # tinkoff-credit accepts rubles
            'quantity': 1,
        }]

    def get_user(self):
        return {
            'contact': {
                'fio': {
                    'lastName': self.user.last_name,
                    'firstName': self.user.first_name,
                },
                'email': self.user.email,
            },
        }

    @property
    def price(self):
        return super().price / 100

    def get_create_order_url(self):
        if settings.TINKOFF_CREDIT_DEMO_MODE:
            return 'https://forma.tinkoff.ru/api/partners/v2/orders/create-demo'

        return 'https://loans.tinkoff.ru/api/partners/v1/lightweight/create'
