from decimal import Decimal
from typing import TYPE_CHECKING

from rest_framework.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from banking.base import Bank

if TYPE_CHECKING:
    from orders.models import Order


class ZeroPriceBank(Bank):
    """Bank used for zero-priced orders, redirects user to URL provided by frontend"""

    currency = "KIS"
    currency_symbol = "💋"
    acquiring_percent = Decimal(0)
    name = _("Zero Price")

    def __init__(
        self,
        order: "Order",
        success_url: str | None = None,
        fail_url: str | None = None,
        idempotency_key: str | None = None,
        redirect_url: str | None = None,
    ) -> None:
        super().__init__(
            order=order,
            success_url=success_url,
            fail_url=fail_url,
            idempotency_key=idempotency_key,
        )
        self.redirect_url = redirect_url

    def validate_order(self, order: "Order") -> None:
        if order.price != 0:
            raise ValidationError("ZeroPriceBank may be used only with zero-priced orders")

    def get_initial_payment_url(self) -> str:
        if self.redirect_url is None:
            raise ValidationError("Please provide redirect_url when using ZeroPriceBank")

        return self.redirect_url
