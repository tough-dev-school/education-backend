from dataclasses import dataclass
from decimal import Decimal
from typing import Type
from urllib.parse import urljoin

from celery import chain
from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property

from apps.amocrm.tasks import amocrm_enabled, push_order, push_user
from apps.banking.base import Bank
from apps.banking.selector import get_bank_or_default
from apps.dashamail import tasks as dashamail
from apps.mailing.tasks import send_mail
from apps.orders.models import Order, PromoCode
from apps.products.models.base import Shippable
from apps.users.models import User
from apps.users.tasks import rebuild_tags
from core.current_user import get_current_user
from core.exceptions import AppServiceException
from core.helpers import lower_first
from core.services import BaseService


class OrderCreatorException(AppServiceException):
    pass


@dataclass
class OrderCreator(BaseService):
    user: User
    item: Shippable
    price: Decimal | None = None
    promocode: str | None = None
    desired_bank: str | None = None
    analytics: dict[str, str | dict] | None = None

    subscribe: bool = False
    push_to_amocrm: bool = True

    def __post_init__(self) -> None:
        self.price = self.price if self.price is not None else self.item.get_price(promocode=self.promocode)
        self.promocode = self._get_promocode(self.promocode)
        self.desired_bank = self.desired_bank if self.desired_bank is not None else ""

    def act(self) -> Order:
        order = self.create()

        order.set_item(self.item)
        order.save()

        self.send_confirmation_message(order)
        self.update_user_tags(order)

        self.do_push_to_amocrm(order)
        self.do_push_to_dashamail(order)
        self.do_push_to_dashamail_directcrm(order)

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
            analytics=self.analytics if self.analytics is not None else dict(),
        )

    @staticmethod
    def _get_promocode(promocode_name: str | None = None) -> PromoCode | None:
        if promocode_name is not None:
            return PromoCode.objects.get_or_nothing(name=promocode_name)

    @cached_property
    def bank(self) -> Type[Bank]:
        return get_bank_or_default(self.desired_bank)

    def send_confirmation_message(self, order: Order) -> None:
        if order.price == 0 and order.item is not None:
            if hasattr(order.item, "confirmation_template_id") and order.item.confirmation_template_id:
                send_mail.delay(
                    to=order.user.email,
                    template_id=order.item.confirmation_template_id,
                    ctx=self._get_confirmation_template_context(order),
                )

    def update_user_tags(self, order: Order) -> None:
        rebuild_tags.delay(student_id=order.user_id)

    def do_push_to_amocrm(self, order: Order) -> None:
        if not self.push_to_amocrm or not amocrm_enabled():
            return

        if order.price <= 0:
            return

        chain(
            push_user.si(user_id=order.user.id),
            push_order.si(order_id=order.id),
        ).apply_async(countdown=10)

    def do_push_to_dashamail(self, order: Order) -> None:
        if self.subscribe and order.user.email and len(order.user.email):
            dashamail.update_subscription.apply_async(
                kwargs={"student_id": order.user.id},
                countdown=30,
            )  # hope rebuild_tags from push_to_amocrm is complete

    def do_push_to_dashamail_directcrm(self, order: Order) -> None:
        chain(
            dashamail.directcrm_subscribe.si(order_id=order.pk),
            dashamail.push_order_event.si(
                event_name="OrderCreated",
                order_id=order.pk,
            ),
        ).delay()

    @staticmethod
    def _get_confirmation_template_context(order: Order) -> dict[str, str]:
        return {
            "item": order.item.full_name,
            "item_lower": lower_first(order.item.full_name),
            "firstname": order.user.first_name,
            "confirmation_url": urljoin(settings.FRONTEND_URL, reverse("confirm-order", args=[order.slug])),
        }
