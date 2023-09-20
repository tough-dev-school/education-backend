from dataclasses import dataclass
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse

from app.pricing import format_price
from app.services import BaseService
from mailing.tasks import send_mail
from orders import human_readable
from orders.models import Order
from orders.models import Refund
from users.models import User
from ipaddress import IPv4Address
from ipaddress import IPv6Address


@dataclass
class OrderRefunder(BaseService):
    order: Order
    author: User
    author_ip: IPv4Address | IPv6Address

    def act(self) -> Refund:
        refund = self.create_refund()

        self.notify()

        return refund

    def create_refund(self) -> Refund:
        return Refund.objects.create(
            order=self.order,
            author=self.author,
            author_ip=str(self.author_ip),
        )

    def notify(self) -> None:
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
            "bank": human_readable.get_order_payment_method_name(self.order),
            "author": str(self.author),
            "author_ip": str(self.author_ip),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }
