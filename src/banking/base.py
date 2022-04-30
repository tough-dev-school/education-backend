from typing import Optional, Union

import uuid
from abc import ABCMeta, abstractmethod
from django.conf import settings
from urllib.parse import urljoin

from orders.models import Order
from users.models import User


class Bank(metaclass=ABCMeta):
    currency = 'RUB'
    currency_symbol = '₽'
    ue: int = 1

    def __init__(
        self,
        order: Order,
        success_url:
        Optional[str] = None,
        fail_url: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> None:
        self.order = order
        self._success_url = success_url
        self._fail_url = fail_url
        self.idempotency_key = idempotency_key or str(uuid.uuid4())

    @abstractmethod
    def get_initial_payment_url(self) -> str:
        raise NotImplementedError()

    @property
    def success_url(self) -> str:
        return self._success_url or urljoin(settings.FRONTEND_URL, '/success/')

    @property
    def fail_url(self) -> str:
        return self._fail_url or urljoin(settings.FRONTEND_URL, '/error/?code=banking')

    @property
    def price(self) -> Union[int, str]:
        from banking import price_calculator
        price = price_calculator.to_bank(bank=self.__class__, price=self.order.price)
        return int(price * 100)

    @property
    def user(self) -> User:
        return self.order.user
