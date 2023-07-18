from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Type
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.functional import cached_property
from django.utils.timezone import is_naive
from django.utils.timezone import make_aware

from app.current_user import get_current_user
from app.exceptions import AppServiceException
from app.helpers import lower_first
from app.services import BaseService
from banking.base import Bank
from banking.selector import get_bank
from mailing.tasks import send_mail
from orders.models import Order
from orders.models import PromoCode
from products.models.base import Shippable
from users.models import User


class OrderCreatorException(AppServiceException):
    pass


@dataclass
class OrderCreator(BaseService):
    user: User
    item: Shippable
    price: Decimal | None = None
    promocode: str | None = None
    desired_bank: str | None = None

    def __post_init__(self) -> None:
        self.price = self.price if self.price is not None else self.item.get_price(promocode=self.promocode)
        self.promocode = self._get_promocode(self.promocode)
        self.desired_bank = self.desired_bank if self.desired_bank is not None else ""

    def act(self) -> Order:
        order = self.create()

        order.set_item(self.item)
        order.save()

        self.send_confirmation_message(order)

        return order

    def create(self) -> Order:
        return Order.objects.create(
            user=self.user,
            author=get_current_user() or self.user,
            price=self.price,  # type: ignore
            promocode=self.promocode,
            bank_id=self.desired_bank,
            ue_rate=self.bank.ue,
            acquiring_percent=self.bank.acquiring_percent,
        )

    @staticmethod
    def _get_promocode(promocode_name: str | None = None) -> PromoCode | None:
        if promocode_name is not None:
            return PromoCode.objects.get_or_nothing(name=promocode_name)

    @cached_property
    def bank(self) -> Type[Bank]:
        return get_bank(self.desired_bank)

    def send_confirmation_message(self, order: Order) -> None:
        if order.price == 0 and order.item is not None:
            if hasattr(order.item, "confirmation_template_id") and order.item.confirmation_template_id:
                send_mail.delay(
                    to=order.user.email,
                    template_id=order.item.confirmation_template_id,
                    ctx=self.get_template_context(order),
                )

    @staticmethod
    def get_template_context(order: Order) -> dict[str, str]:
        return {
            "item": order.item.full_name,
            "item_lower": lower_first(order.item.full_name),
            "firstname": order.user.first_name,
            "confirmation_url": urljoin(settings.FRONTEND_URL, reverse("confirm-order", args=[order.slug])),
        }

    @staticmethod
    def make_datetime_aware(input_dt: str | datetime | None = None) -> datetime | None:
        """Return timezone aware datetime.datetime or None.

        Supports time zone offsets. When the input contains one, the output uses a timezone
        with a fixed offset from UTC. If timezone offset was not provided use default timezone."""
        if input_dt is None:
            return None

        parsed_dt = parse_datetime(input_dt) if isinstance(input_dt, str) else input_dt

        if parsed_dt is None:
            raise OrderCreatorException("Input is not ISO formatted and could not be converted to datetime.")

        return make_aware(parsed_dt) if is_naive(parsed_dt) else parsed_dt
