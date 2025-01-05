import uuid
from abc import ABCMeta, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.banking.exceptions import AcquiringDoesNotExist, CurrencyRateDoesNotExist
from apps.banking.models import Acquiring, CurrencyRate

if TYPE_CHECKING:
    from django_stubs_ext import StrPromise

    from apps.orders.models import Order
    from apps.users.models import User


class Bank(metaclass=ABCMeta):
    currency = "RUB"
    currency_symbol = "₽"
    name: "StrPromise" = _("—")
    bank_id: str = "—"

    def __init__(
        self,
        order: "Order",
        success_url: str | None = None,
        fail_url: str | None = None,
        idempotency_key: str | None = None,
        **kwargs: str | None,
    ) -> None:
        self.order = order
        self._success_url = success_url
        self._fail_url = fail_url
        self.idempotency_key = idempotency_key or str(uuid.uuid4())

        self.validate_order(order=self.order)

    @abstractmethod
    def get_initial_payment_url(self) -> str:
        raise NotImplementedError()

    def refund(self, amount: Decimal | None = None) -> None:
        return

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
        return self.get_formatted_amount(self.order.price)

    @property
    def user(self) -> "User":
        return self.order.user

    @property
    def is_partial_refund_available(self) -> bool:
        return False

    @classmethod
    def get_currency_rate(cls) -> Decimal:
        try:
            return CurrencyRate.objects.get(name=cls.currency).rate
        except CurrencyRate.DoesNotExist:
            raise CurrencyRateDoesNotExist(f"Currency {cls.currency} is not supported")

    @classmethod
    def get_acquiring_percent(cls) -> Decimal:  # we use it for analytics
        try:
            return Acquiring.objects.get(bank=cls.bank_id).percent
        except Acquiring.DoesNotExist:
            raise AcquiringDoesNotExist(f"Acquiring percent for {cls.name} is not supported")

    def get_formatted_amount(self, amount: Decimal) -> int:
        from apps.banking import price_calculator

        price = price_calculator.to_bank(bank=self.__class__, price=amount)
        return int(price * 100)
