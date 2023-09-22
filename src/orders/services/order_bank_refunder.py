from dataclasses import dataclass
from datetime import timedelta
from typing import Callable
from urllib.parse import urljoin

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from app.current_user import get_current_user
from app.pricing import format_price
from app.services import BaseService
from banking.selector import get_bank
from banking.selector import REFUNDABLE_BANK_KEYS
from mailing.tasks import send_mail
from orders.models import Order
from orders.models import RefundLogEntry
from users.models import User


class OrderRefunderException(Exception):
    pass


@dataclass
class OrderBankRefunder(BaseService):
    """Refund the order in the bank, mark it as not paid and notify about that."""

    order: Order

    @cached_property
    def author(self) -> User:
        return get_current_user()  # type: ignore

    def act(self) -> Order:
        with transaction.atomic():
            self.do_bank_refund(self.order)
            self.mark_not_paid_and_log()

        self.notify_dangerous_operation_happened()

        return self.order

    def mark_not_paid_and_log(self) -> RefundLogEntry:
        self.order.paid = None
        self.order.save(update_fields=["paid", "modified"])

        return RefundLogEntry.objects.create(
            order=self.order,
            author=self.author,
        )

    def do_bank_refund(self, order: Order) -> None:
        """Do bank API call here"""

    def notify_dangerous_operation_happened(self) -> None:
        for email in settings.DANGEROUS_OPERATION_HAPPENED_EMAILS:
            send_mail.delay(
                to=email,
                template_id="order-refunded",
                ctx=self.get_template_context(),
            )

    def get_template_context(self) -> dict:
        return {
            "refunded_item": self.order.item.name,
            "price": format_price(self.order.price),
            "bank": get_bank(self.order.bank_id).name,
            "author": str(self.author),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order,
            self.validate_current_user,
            self.validate_refunds_rate_limit,
        ]

    def validate_order(self) -> None:
        if self.order.bank_id not in REFUNDABLE_BANK_KEYS:
            raise OrderRefunderException("The order couldn't be bank refunded please call OrderUnpaidSetter")

        if not self.order.paid or RefundLogEntry.objects.filter(order=self.order).exists():
            raise OrderRefunderException("The order is not paid or refunded already")

    def validate_current_user(self) -> None:
        if get_current_user() is None:
            raise OrderRefunderException("Can't get the user")  # it's likely a programmable error

    def validate_refunds_rate_limit(self) -> None:
        count_author_refunds_in_last_24_hours = RefundLogEntry.objects.filter(
            author=self.author,
            created__gte=timezone.now() - timedelta(hours=24),
        ).count()

        if count_author_refunds_in_last_24_hours >= 5:
            raise OrderRefunderException("To many refunds in last 24 hours")
