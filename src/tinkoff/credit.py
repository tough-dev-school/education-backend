import httpx

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from banking.base import Bank


class TinkoffCreditRequestException(Exception):
    pass


class TinkoffCredit(Bank):
    name = _("Tinkoff Credit")

    def get_initial_payment_url(self) -> str:
        result = self.call(
            url=self.get_create_order_url(),
            payload={
                "shopId": settings.TINKOFF_CREDIT_SHOP_ID,
                "showcaseId": settings.TINKOFF_CREDIT_SHOWCASE_ID,
                "sum": self.price,
                "orderNumber": self.order.slug,
                "promoCode": self.order.item.tinkoff_credit_promo_code or None,
                "values": self.get_user(),
                "items": self.get_items(),
            },
        )

        return result["link"]

    def call(self, url: str, payload: dict) -> dict:
        """Query TinkoffCredit API"""
        response = httpx.post(url, json=payload)

        if response.status_code != 200:
            errors = response.json()["errors"]
            raise TinkoffCreditRequestException(f"Incorrect HTTP-status code for {url}: {response.status_code}, {errors}")

        return response.json()

    def get_items(self) -> list[dict[str, str | int]]:
        return [
            {
                "name": self.order.item.name_receipt,
                "price": self.price,  # tinkoff-credit accepts rubles
                "quantity": 1,
            },
        ]

    def get_user(self) -> dict:
        return {
            "contact": {
                "fio": {
                    "lastName": self.user.last_name,
                    "firstName": self.user.first_name,
                },
                "email": self.user.email,
            },
        }

    @property
    def price(self) -> int:
        return super().price / 100  # type: ignore

    def get_create_order_url(self) -> str:
        if settings.TINKOFF_CREDIT_DEMO_MODE:
            return "https://forma.tinkoff.ru/api/partners/v2/orders/create-demo"

        return "https://forma.tinkoff.ru/api/partners/v2/orders/create"
