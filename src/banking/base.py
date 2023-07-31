from abc import ABCMeta
from abc import abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING
from urllib.parse import urljoin
import uuid

from django.conf import settings

if TYPE_CHECKING:
    from orders.models import Order
    from users.models import User


class Bank(metaclass=ABCMeta):
    currency = "RUB"
    currency_symbol = "₽"
    ue: int = 1  # ue stands for «условные единицы», this is some humour from 2000's
    acquiring_percent: Decimal = Decimal(0)  # we use it for analytics
    name: str = "—"

    def __init__(
        self,
        order: "Order",
        success_url: str | None = None,
        fail_url: str | None = None,
        idempotency_key: str | None = None,
    ) -> None:
        self.order = order
        self._success_url = success_url
        self._fail_url = fail_url
        self.idempotency_key = idempotency_key or str(uuid.uuid4())

        self.validate_order(order=self.order)

    @abstractmethod
    def get_initial_payment_url(self) -> str:
        raise NotImplementedError()

    def validate_order(self, order: "Order") -> None:  # NOQA: B027
        """Hook to validate if order suites given bank"""
        return

    @property
    def success_url(self) -> str:
        return self._success_url or urljoin(settings.FRONTEND_URL, "/success/")

    @property
    def fail_url(self) -> str:
        return self._fail_url or urljoin(settings.FRONTEND_URL, "/error/?code=banking")

    @property
    def price(self) -> int | str:
        from banking import price_calculator

        price = price_calculator.to_bank(bank=self.__class__, price=self.order.price)
        return int(price * 100)

    @property
    def user(self) -> "User":
        return self.order.user

    def successful_payment_callback(self) -> None:  # NOQA: B027
        ...
