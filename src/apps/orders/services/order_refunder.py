from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from apps.banking.base import Bank
from apps.banking.selector import get_bank
from apps.dashamail import tasks as dashamail
from apps.mailing import tasks as mailing_tasks
from apps.orders import human_readable
from apps.orders.models import Order
from apps.orders.models.refund import Refund
from apps.orders.services.order_unshipper import OrderUnshipper
from apps.users.models import User
from apps.users.tasks import rebuild_tags
from core.current_user import get_current_user
from core.exceptions import AppServiceException
from core.pricing import format_price
from core.services import BaseService
from core.tasks import write_admin_log


class OrderRefunderException(AppServiceException):
    pass


@dataclass
class OrderRefunder(BaseService):
    """Refund and unship order.

    If order is not paid just unship and register in integrations.
    If order is paid and is suitable for bank refund - do it.
    If amount is not specified - refund full available to refund amount.
    Available to refund amount = initial order price - already refunded amount.
    """

    order: Order
    author: User
    amount: Decimal | None = None

    def __post_init__(self) -> None:
        self.payment_method_before_service_call = human_readable.get_order_payment_method_name(self.order)

    @cached_property
    def bank(self) -> Bank | None:
        Bank = get_bank(self.order.bank_id)
        return Bank(order=self.order) if Bank else None

    def act(self) -> None:
        self.amount_to_refund = self.get_amount_to_refund()

        if self.order.paid:
            self.create_refund_entry()
            self.do_bank_refund_if_needed()
            self.mark_order_as_not_paid_if_needed()

        if not self.order.paid:  # if afterward order was fully refunded or was never paid
            OrderUnshipper(order=self.order)()

        self.write_success_admin_log()
        self.notify_dangerous_operation_happened()

        self.update_user_tags()
        self.update_dashamail()

    def validate(self) -> None:
        if self.amount and self.amount != self.order.price and self.bank and not self.bank.is_partial_refund_available:
            raise OrderRefunderException(_("Partial refund is not available"))
        if self.amount and self.order.available_to_refund_amount < self.amount:
            raise OrderRefunderException(_("Amount to refund is more than available"))

    def get_amount_to_refund(self) -> Decimal:
        """
        Using this in email.
        Not using self.order.price for total refund because order can already be partially refunded.
        """
        return self.amount or self.order.available_to_refund_amount

    def create_refund_entry(self) -> None:
        Refund.objects.create(order=self.order, author=self.author, amount=self.amount_to_refund)

    def mark_order_as_not_paid_if_needed(self) -> None:
        if self.order.available_to_refund_amount == 0:
            self.order.paid = None
            self.order.unpaid = timezone.now()
            self.order.save(update_fields=["paid", "unpaid", "modified"])

    def do_bank_refund_if_needed(self) -> None:
        if self.bank and settings.BANKS_REFUNDS_ENABLED:
            self.bank.refund(self.amount)

    def write_success_admin_log(self) -> None:
        write_admin_log.delay(
            action_flag=CHANGE,
            app="orders",
            change_message=f"Order refunded: refunded amount: {format_price(self.amount or self.amount_to_refund)}, available to refund: {format_price(self.order.available_to_refund_amount)}",
            model="Order",
            object_id=self.order.id,
            user_id=get_current_user().id,  # type: ignore[union-attr]
        )

    def update_user_tags(self) -> None:
        rebuild_tags.delay(student_id=self.order.user_id)

    def update_dashamail(self) -> None:
        dashamail.update_subscription.apply_async(
            kwargs={"student_id": self.order.user_id},
            countdown=30,
        )  # hope rebuild_tags from update_user_tags is complete

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
            "refund_author": str(get_current_user()),
            "payment_method_name": self.payment_method_before_service_call,
            "price": format_price(self.order.price),
            "amount": format_price(self.amount_to_refund),
            "available_to_refund": format_price(self.order.available_to_refund_amount),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }
