from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from django.conf import settings

from app.services import BaseService
from banking.atol import exceptions
from banking.atol.auth import get_atol_token
from orders.models import Order

BASE_URL = "https://online.atol.ru/possystem/v4/"


@dataclass
class AtolClient(BaseService):
    order: Order

    def act(self) -> None:
        self.post(
            method="sell",
            payload={
                "external_id": self.order.slug,
                "timestamp": self.order.created.strftime("%d.%m.%Y %H:%M:%S"),
                "receipt": {
                    "client": {
                        "email": self.order.user.email,
                    },
                    "company": {
                        "email": settings.RECEIPTS_EMAIL,
                        "inn": settings.VAT_ID,
                        "payment_address": settings.ATOL_PAYMENT_ADDRESS,
                    },
                    "items": self.get_items(),
                    "total": self.get_item_price(),
                    "payments": [
                        {
                            "type": 1,
                            "sum": self.get_item_price(),
                        },
                    ],
                },
                "service": {
                    "callback_url": self.get_callback_url(),
                },
            },
        )

    def post(self, method: str, payload: dict) -> dict:
        """Query Dolyame API"""
        response = httpx.post(
            url=urljoin(BASE_URL, f"{settings.ATOL_GROUP_CODE}/{method}"),
            json=payload,
            headers={
                "Token": get_atol_token(),
            },
        )

        if response.status_code != 200:
            data = response.json()
            raise exceptions.AtolHTTPError("Atol HTTP %s, error: %s (code: %s)", response.status_code, data["error"]["text"], data["error"]["error_id"])

        return response.json()

    def get_items(self) -> list[dict]:
        return [
            {
                "name": self.order.item.name_receipt,
                "price": self.get_item_price(),
                "sum": self.get_item_price(),
                "quantity": 1,
                "payment_method": "full_payment",
                "payment_object": "service",
                "vat": {
                    "type": "none",
                },
            },
        ]

    def get_item_price(self) -> int:
        """Atol API does not support strigified numbers, and i can't figure out how the send them as integers.

        The code that should be here is:
            return str(round(Decimal(self.order.price), 2))  # 100500 -> 100500.00

        But we use
        """
        return int(self.order.price)

    @staticmethod
    def get_callback_url() -> str:
        return urljoin(settings.ABSOLUTE_HOST, f"/api/v2/banking/atol-webhooks-{settings.ATOL_WEBHOOK_SALT}")


__all__ = [
    "AtolClient",
]
