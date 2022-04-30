import httpx
from decimal import Decimal
from django.conf import settings
from urllib.parse import urljoin

from banking.base import Bank


class DolyameRequestException(Exception):
    pass


class Dolyame(Bank):
    base_url = 'https://partner.dolyame.ru/v1/'

    def get_initial_payment_url(self) -> str:
        result = self.post(
            method='orders/create',
            payload={
                'order': {
                    'id': self.order_id,
                    'amount': self.price,
                    'items': self.get_items(),
                },
                'client_info': self.get_client_info(),
                'notification_url': self.get_notification_url(),
                'success_url': self.success_url,
                'fail_url': self.fail_url,
            },
        )

        return result['link']

    def commit(self) -> None:
        self.post(
            method=f'orders/{self.order_id}/commit',
            payload={
                'amount': self.price,
                'items': self.get_items(),
            },
        )

    def post(self, method: str, payload: dict) -> dict:
        """Query Dolyame API
        """
        response = httpx.post(
            url=urljoin(self.base_url, method),
            json=payload,
            auth=(settings.DOLYAME_LOGIN, settings.DOLYAME_PASSWORD),
            headers={
                'X-Correlation-ID': self.idempotency_key,
            },
            cert=settings.DOLYAME_CERTIFICATE_PATH,
        )

        if response.status_code != 200:
            raise DolyameRequestException(f'Incorrect HTTP-status code for {method}: {response.status_code}')

        return response.json()

    def get_items(self) -> list[dict]:
        return [
            {
                'name': self.order.item.name_receipt,
                'price': self.price,
                'quantity': 1,
            },
        ]

    def get_client_info(self) -> dict:
        return {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
        }

    @property
    def price(self) -> str:
        return str(Decimal(super().price / 100))  # type: ignore

    @property
    def order_id(self) -> str:
        return f'tds-{self.order.id}'

    @staticmethod
    def get_notification_url() -> str:
        return urljoin(settings.ABSOLUTE_HOST, '/api/v2/banking/dolyame-notifications/')
