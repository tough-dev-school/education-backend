from dataclasses import dataclass
from datetime import timedelta
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from typing import Callable
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from app.pricing import format_price
from app.services import BaseService
from banking.selector import get_bank
from banking.zero_price_bank import ZeroPriceBank
from mailing.tasks import send_mail
from orders.models import Order
from orders.models import Refund
from orders.services.order_unpaid_setter import OrderUnpaidSetter
from users.models import User


class OrderRefunderException(Exception):
    pass


@dataclass
class OrderRefunder(BaseService):
    order: Order
    author: User
    author_ip: IPv4Address | IPv6Address

    def act(self) -> Refund:
        OrderUnpaidSetter(self.order)()

        refund = self.create_refund_entry()
        self.do_bank_refund(refund)
        self.notify_dangerous_operation_happened()

        return refund

    def create_refund_entry(self) -> Refund:
        return Refund.objects.create(
            order=self.order,
            author=self.author,
            author_ip=str(self.author_ip),
        )

    def do_bank_refund(self, refund: Refund) -> None:
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
            "author_ip": str(self.author_ip),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_refunds_rate_limit,
            self.validate_order,
        ]

    def validate_refunds_rate_limit(self) -> None:
        count_author_refunds_in_last_24_hours = Refund.objects.filter(
            author=self.author,
            created__gte=timezone.now() - timedelta(hours=24),
        ).count()

        if count_author_refunds_in_last_24_hours >= 5:
            raise OrderRefunderException("To many refunds in last 24 hours")

    def validate_order(self) -> None:
        if not self.order.paid:
            raise OrderRefunderException("Order is not paid")

        if get_bank(self.order.bank_id) == ZeroPriceBank or self.order.price == 0:
            raise OrderRefunderException("The order if free, no refund possible")

        if Refund.objects.filter(order=self.order, created__gte=self.order.paid).exists():
            raise OrderRefunderException("Order already refunded")
