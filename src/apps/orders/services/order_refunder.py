from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.banking.base import Bank
from apps.banking.selector import get_bank
from apps.dashamail import tasks as dashamail
from apps.mailing import tasks as mailing_tasks
from apps.orders import human_readable
from apps.orders.models import Order, Refund
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
    Available to refund amount = initial order price - already refunded amount.
    """

    order: Order
    amount: Decimal

    def __post_init__(self) -> None:
        self.payment_method_before_service_call = human_readable.get_order_payment_method_name(self.order)

    @property
    def refund_author(self) -> User:
        return get_current_user()  # type: ignore

    @property
    def bank(self) -> Bank | None:
        Bank = get_bank(self.order.bank_id)
        return Bank(order=self.order) if Bank else None

    @transaction.atomic
    def act(self) -> "Refund":
        refund = self.create_refund_entry()

        # Update price so we don't include refunded amount in finance dashboards
        # Order price equals to initial price minus refunded amount
        self.update_price()

        if self.amount != 0:
            self.do_bank_refund()

        # If afterward order was fully refunded or was never paid
        if not self.order.paid or self.order.price == 0:
            OrderUnshipper(order=self.order)()

        self.write_success_admin_log()
        self.notify_dangerous_operation_happened()

        self.update_user_tags()
        self.update_dashamail()
        return refund

    def get_validators(self) -> list:
        return [
            self.validate_throttling,
            self.validate_partial_available,
            self.validate_amount,
        ]

    def validate_throttling(self) -> None:
        if Refund.objects.last_ten_seconds(order_id=self.order.pk).count() >= 1:
            raise OrderRefunderException(_("Order has not been refunded. Up to 1 refund per 10 seconds is allowed. Please try again later."))
        if Refund.objects.today().count() >= 5:
            raise OrderRefunderException(_("Order has not been refunded. Up to 5 refunds per day are allowed. Please come back tomorrow."))

    def validate_partial_available(self) -> None:
        partial_available = self.bank.is_partial_refund_available if self.bank else True

        if self.order.paid and self.amount != self.order.price is not None and not partial_available:
            raise OrderRefunderException(_("Partial refund is not available"))

    def validate_amount(self) -> None:
        if self.amount > 0 and not self.order.paid:
            raise OrderRefunderException(_("Only 0 can be refunded for not paid order"))
        if self.order.price < self.amount:
            raise OrderRefunderException(_("Amount to refund is more than available"))
        if self.amount < 0:
            raise OrderRefunderException(_("Amount to refund should be more or equal 0"))

    def create_refund_entry(self) -> Refund:
        return Refund.objects.create(
            order=self.order,
            author=self.refund_author,
            amount=self.amount,
            bank_id=self.order.bank_id,
        )

    def do_bank_refund(self) -> None:
        if self.amount and self.bank and settings.BANKS_REFUNDS_ENABLED:
            self.bank.refund(self.amount)

    def write_success_admin_log(self) -> None:
        write_admin_log.delay(
            action_flag=CHANGE,
            app="orders",
            change_message=f"Order refunded: refunded amount - {format_price(self.amount)}",
            model="Order",
            object_id=self.order.id,
            user_id=self.refund_author.id,
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
            "refund_author": str(self.refund_author),
            "payment_method_name": self.payment_method_before_service_call,
            "price": format_price(self.order.price),
            "amount": format_price(self.amount),
            "order_admin_site_url": urljoin(
                settings.ABSOLUTE_HOST,
                reverse("admin:orders_order_change", args=[self.order.pk]),
            ),
        }

    def update_price(self) -> None:
        self.order.price = self.order.price - self.amount
        self.order.save(update_fields=["modified", "price"])
