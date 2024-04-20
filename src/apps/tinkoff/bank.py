from collections import OrderedDict
from decimal import Decimal
from hashlib import sha256
from typing import Any
from urllib.parse import urljoin

import httpx
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank
from apps.tinkoff.exceptions import TinkoffRequestException


class TinkoffBank(Bank):
    acquiring_percent = Decimal("2.49")
    name = _("Tinkoff")

    @property
    def is_partial_refund_available(self) -> bool:
        return True

    def get_initial_payment_url(self) -> str:
        return self.Init()["PaymentURL"]

    def refund(self, amount: Decimal | None = None) -> None:
        last_payment_notification = self.order.tinkoff_payment_notifications.order_by("-id")[0]

        formatted_amount = self.get_formatted_amount(amount) if amount else self.price
        refund_amount_data = {"Amount": formatted_amount} if amount else {}

        self.call(
            "Cancel",
            payload={
                "PaymentId": last_payment_notification.payment_id,
                "Receipt": self.get_receipt(formatted_amount),  # type: ignore
                **refund_amount_data,
            },
        )

    def Init(self) -> dict:
        return self.call(
            "Init",
            payload={
                "Amount": self.price,
                "OrderId": self.order.slug,
                "CustomerKey": self.user.id,
                "SuccessURL": self.success_url,
                "FailURL": self.fail_url,
                "Receipt": self.get_receipt(self.price),  # type: ignore
                "NotificationURL": self.get_notification_url(),
            },
        )

    def call(self, method: str, payload: dict) -> dict:
        """Query Tinkoff API"""
        payload.update({"TerminalKey": settings.TINKOFF_TERMINAL_KEY})

        response = httpx.post(
            f"https://securepay.tinkoff.ru/v2/{method}/",
            json={
                "Token": self._get_token(payload),
                **payload,
            },
        )

        if response.status_code != 200:
            raise TinkoffRequestException(f"Incorrect HTTP-status code for {method}: {response.status_code}")

        parsed = response.json()

        if not parsed["Success"]:
            raise TinkoffRequestException(f'Non-success request for {method}: {parsed["ErrorCode"]}, {parsed["Message"]} ({parsed["Details"]}')

        return parsed

    def get_receipt(self, amount: int) -> dict[str, Any]:
        return {
            "Email": self.user.email,
            "Taxation": "usn_income",
            "Items": self.get_items(amount),
        }

    def get_items(self, amount: int) -> list[dict[str, Any]]:
        return [
            {
                "Name": self.order.item.name_receipt,
                "Price": amount,
                "Quantity": 1,
                "Amount": amount,
                "PaymentObject": "service",
                "Tax": "none",  # fuck
            },
        ]

    @staticmethod
    def _get_token(request: dict) -> str:
        """Get request signature based on https://oplata.tinkoff.ru/landing/develop/documentation/request_sign"""
        _request = request.copy()

        for key_to_ignore in ["DATA", "Receipt"]:
            _request.pop(key_to_ignore, None)

        _request["Password"] = settings.TINKOFF_TERMINAL_PASSWORD

        sorted_request = OrderedDict(sorted(_request.items(), key=lambda key, *args: key))
        return sha256("".join(str(value) for value in sorted_request.values()).encode()).hexdigest()

    @staticmethod
    def get_notification_url() -> str:
        return urljoin(settings.ABSOLUTE_HOST, "/api/v2/banking/tinkoff-notifications/")
