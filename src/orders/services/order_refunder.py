from dataclasses import dataclass
from urllib.parse import urljoin

import celery

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from amocrm.tasks import amocrm_enabled
from amocrm.tasks import push_user
from amocrm.tasks import return_order
from app.current_user import get_current_user
from app.pricing import format_price
from app.services import BaseService
from banking.base import Bank
from banking.selector import get_bank
from mailing import tasks as mailing_tasks
from orders.models import Order
from orders.services.order_unshipper import OrderUnshipper
from users.tasks import rebuild_tags


class OrderRefunderException(Exception):
    pass


@dataclass
class OrderRefunder(BaseService):
    """Refund and unship order.

    If order is not paid just unship and register in integrations.
    If order is paid and is suitable for bank refund - do it.
    """

    order: Order

    @cached_property
    def bank(self) -> Bank | None:
        if self.order.bank_id:
            return get_bank(self.order.bank_id)(order=self.order)

    def act(self) -> None:
        if self.order.paid and settings.BANKS_REFUNDS_ENABLED:
            is_bank_refunded = self.do_bank_refund_if_needed()
            self.notify_dangerous_operation_happened(is_bank_refunded)

        if self.order.paid:
            self.mark_order_as_not_paid()

        OrderUnshipper(order=self.order)()

        self.update_integrations()

    def mark_order_as_not_paid(self) -> None:
        self.order.paid = None
        self.order.unpaid = timezone.now()
        self.order.save(update_fields=["paid", "unpaid", "modified"])

    def do_bank_refund_if_needed(self) -> bool:
        if self.bank:
            self.bank.refund()
            return True

        return False

    def update_integrations(self) -> None:
        can_be_subscribed = bool(self.order.user.email and len(self.order.user.email))

        if not can_be_subscribed and not amocrm_enabled():
            rebuild_tags.delay(student_id=self.order.user.id, subscribe=False)
            return None

        if amocrm_enabled():
            celery.chain(
                rebuild_tags.si(student_id=self.order.user.id, subscribe=can_be_subscribed),
                push_user.si(user_id=self.order.user.id),
                return_order.si(order_id=self.order.id),
            ).delay()

    def notify_dangerous_operation_happened(self, is_bank_refunded: bool) -> None:
        email_context = self.get_email_template_context(is_bank_refunded)

        for email in settings.DANGEROUS_OPERATION_HAPPENED_EMAILS:
            mailing_tasks.send_mail.delay(
                to=email,
                template_id="order-refunded",
                ctx=email_context,
                disable_antispam=True,
            )

    def get_email_template_context(self, is_bank_refunded: bool) -> dict:
        return {
            "order_id": self.order.pk,
            "refunded_item": self.order.item.name if self.order.item else "not-set",
            "refund_author": str(get_current_user() or "unknown"),
            "bank_name": self.bank.name if self.bank else "not-set",
            "is_bank_refunded": is_bank_refunded,
            "price": format_price(self.order.price),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }
