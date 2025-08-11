import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Type
from urllib.parse import urljoin

from celery import chain
from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property

from apps.amocrm.tasks import amocrm_enabled, push_order, push_user
from apps.b2b.models import Deal
from apps.banking.base import Bank
from apps.banking.selector import get_bank_or_default
from apps.dashamail import tasks as dashamail
from apps.dashamail.enabled import dashamail_enabled
from apps.mailing.tasks import send_mail
from apps.orders.models import Order, PromoCode
from apps.products.models import Course
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
    item: Course
    price: Decimal | None = None
    author: User | None = None
    promocode: str | None = None
    desired_bank: str | None = None
    analytics: str | None = None
    deal: Deal | None = None
    raw: dict | None = None

    def __post_init__(self) -> None:
        self.price = self.price if self.price is not None else self.item.price
        self.promocode = self._get_promocode(self.promocode)
        if self.promocode is not None:
            self.price = self.promocode.apply(self.item)

        self.desired_bank = self.desired_bank if self.desired_bank is not None else ""

    def get_author(self) -> User:
        """Author (seller) of the order.
        1. Particular author, e.g. when creating order from the b2b deal
        2. Current user, e.g. when creating order from the admin interface
        3. Student himself, self-ordering from the website
        """

        return next(author for author in [self.author, get_current_user(), self.user] if author is not None)

    def act(self) -> Order:
        order = self.create()

        order.set_item(self.item)
        order.save()

        self.save_acquring_details(order)

        self.send_confirmation_message(order)
        self.update_user_tags(order)

        if amocrm_enabled():
            self.push_to_amocrm(order)

        if dashamail_enabled():
            self.push_to_dashamail(order)
            self.push_to_dashamail_directcrm(order)

        return order

    def create(self) -> Order:
        return Order.objects.create(
            user=self.user,
            author=self.get_author(),
            price=self.price,  # type: ignore
            promocode=self.promocode,
            deal=self.deal,
            bank_id=self.desired_bank,
            analytics=self._parse_analytics(self.analytics),
            raw=self.raw if self.raw is not None else {},
        )

    @staticmethod
    def _parse_analytics(input: str | None) -> dict:
        if input is None:
            return {}

        try:
            return json.loads(input)
        except json.JSONDecodeError:
            return {}

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

    def save_acquring_details(self, order: Order) -> None:
        bank = self.bank(order)
        order.acquiring_percent = bank.get_acquiring_percent()
        order.ue_rate = bank.get_currency_rate()

        order.save(update_fields=["modified", "acquiring_percent", "ue_rate"])

    @staticmethod
    def update_user_tags(order: Order) -> None:
        rebuild_tags.delay(student_id=order.user_id)

    def push_to_amocrm(self, order: Order) -> None:
        if order.price <= 0:
            return

        chain(
            push_user.si(user_id=order.user.id),
            push_order.si(order_id=order.id),
        ).apply_async(countdown=10)

    def push_to_dashamail(self, order: Order) -> None:
        if order.user.email and len(order.user.email):
            dashamail.update_subscription.apply_async(
                kwargs={"student_id": order.user.id},
                countdown=30,
            )  # hope rebuild_tags from push_to_amocrm is complete

    def push_to_dashamail_directcrm(self, order: Order) -> None:
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
