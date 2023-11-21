from dataclasses import dataclass
from urllib.parse import urljoin

import celery

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from apps.amocrm.tasks import amocrm_enabled
from apps.amocrm.tasks import push_user
from apps.amocrm.tasks import return_order
from apps.banking.base import Bank
from apps.banking.selector import get_bank
from apps.mailing import tasks as mailing_tasks
from apps.orders import human_readable
from apps.orders.models import Order
from apps.orders.services.order_unshipper import OrderUnshipper
from apps.users.tasks import rebuild_tags
from core.current_user import get_current_user
from core.pricing import format_price
from core.services import BaseService


@dataclass
class OrderRefunder(BaseService):
    """Refund and unship order.

    If order is not paid just unship and register in integrations.
    If order is paid and is suitable for bank refund - do it.
    """

    order: Order

    def __post_init__(self) -> None:
        self.payment_method_before_service_call = human_readable.get_order_payment_method_name(self.order)

    @cached_property
    def bank(self) -> Bank | None:
        Bank = get_bank(self.order.bank_id)
        return Bank(order=self.order) if Bank else None

    def act(self) -> None:
        if self.order.paid:
            self.do_bank_refund_if_needed()
            self.mark_order_as_not_paid()

        OrderUnshipper(order=self.order)()
        self.notify_dangerous_operation_happened()
        self.update_integrations()

    def mark_order_as_not_paid(self) -> None:
        self.order.paid = None
        self.order.unpaid = timezone.now()
        self.order.save(update_fields=["paid", "unpaid", "modified"])

    def do_bank_refund_if_needed(self) -> None:
        if self.bank and settings.BANKS_REFUNDS_ENABLED:
            self.bank.refund()

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

    def notify_dangerous_operation_happened(self) -> None:
        if not settings.BANKS_REFUNDS_ENABLED:
            return

        email_context = self.get_email_template_context()

        for email in settings.DANGEROUS_OPERATION_HAPPENED_EMAILS:
            mailing_tasks.send_mail.delay(
                to=email,
                template_id="order-refunded",
                ctx=email_context,
                disable_antispam=True,
            )

    def get_email_template_context(self) -> dict:
        return {
            "order_id": self.order.pk,
            "refunded_item": self.order.item.name if self.order.item else "not-set",
            "refund_author": str(get_current_user() or "unknown"),
            "payment_method_name": self.payment_method_before_service_call,
            "price": format_price(self.order.price),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }
