from decimal import Decimal
from urllib.parse import urljoin

import httpx

from django.conf import settings

from banking.base import Bank
from banking.tasks import print_atol_receipt


class DolyameRequestException(Exception):
    pass


class Dolyame(Bank):
    acquiring_percent = Decimal("6.9")
    base_url = "https://partner.dolyame.ru/v1/"
    name = "Долями"
    bank_id = "dolyame"

    def get_initial_payment_url(self) -> str:
        result = self.post(
            method="orders/create",
            payload={
                "order": {
                    "id": self.order.slug,
                    "amount": self.price,
                    "items": self.get_items(),
                },
                "client_info": self.get_client_info(),
                "notification_url": self.get_notification_url(),
                "success_url": self.success_url,
                "fail_url": self.fail_url,
            },
        )

        return result["link"]

    def commit(self) -> None:
        self.post(
            method=f"orders/{self.order.slug}/commit",
            payload={
                "amount": self.price,
                "items": self.get_items(),
            },
        )

    def refund(self) -> None:
        self.post(
            method=f"orders/{self.order.slug}/refund",
            payload={
                "amount": self.price,
                "returned_items": self.get_items(),
            },
        )

    def successful_payment_callback(self) -> None:
        """We have to manualy print reciepts for this payment method"""
        print_atol_receipt.delay(order_id=self.order.pk)

    def post(self, method: str, payload: dict) -> dict:
        """Query Dolyame API"""
        response = httpx.post(
            url=urljoin(self.base_url, method),
            json=payload,
            auth=(settings.DOLYAME_LOGIN, settings.DOLYAME_PASSWORD),
            headers={
                "X-Correlation-ID": self.idempotency_key,
            },
            cert=settings.DOLYAME_CERTIFICATE_PATH,
        )

        if response.status_code != 200:
            raise DolyameRequestException(f"Incorrect HTTP-status code for {method}: {response.status_code}")

        return response.json()

    def get_items(self) -> list[dict]:
        return [
            {
                "name": self.order.item.name_receipt,
                "price": self.price,
                "quantity": 1,
            },
        ]

    def get_client_info(self) -> dict:
        return {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
        }

    @property
    def price(self) -> str:
        return str(Decimal(super().price / 100))  # type: ignore

    @staticmethod
    def get_notification_url() -> str:
        return urljoin(settings.ABSOLUTE_HOST, "/api/v2/banking/dolyame-notifications/")
