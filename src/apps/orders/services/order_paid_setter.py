from dataclasses import dataclass

from celery import chain
from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.utils import timezone

from apps.amocrm.tasks import amocrm_enabled, push_order, push_user
from apps.dashamail import tasks as dashamail
from apps.orders import human_readable
from apps.orders.models import Order
from apps.users.tasks import rebuild_tags
from core.current_user import get_current_user
from core.services import BaseService
from core.tasks import send_telegram_message, write_admin_log


@dataclass
class OrderPaidSetter(BaseService):
    """Mark order as paid"""

    order: Order
    silent: bool | None = False

    def __post_init__(self) -> None:
        """Save order state at boot time"""
        self.is_already_paid = self.order.paid is not None
        self.is_already_shipped = self.order.shipped is not None

    def act(self) -> None:
        self.mark_order_as_paid()
        self.ship()

        self.write_success_admin_log()
        self.send_happiness_message()

        self.rebuild_user_tags()
        self.update_amocrm()
        self.update_dashamail()
        self.update_dashamail_directcrm()

    def mark_order_as_paid(self) -> None:
        self.order.paid = timezone.now()

        self.order.save(update_fields=["paid", "modified"])

    def ship(self) -> None:
        if not self.is_already_shipped and not self.is_already_paid and self.order.item is not None:
            self.order.ship()

    def rebuild_user_tags(self) -> None:
        rebuild_tags.delay(student_id=self.order.user_id)

    def update_amocrm(self) -> None:
        if amocrm_enabled():
            chain(
                push_user.si(user_id=self.order.user_id),
                push_order.si(order_id=self.order.id),
            ).apply_async(countdown=30)  # hope tags are rebuilt by this time

    def update_dashamail(self) -> None:
        dashamail.update_subscription.apply_async(
            kwargs=dict(student_id=self.order.user_id),
            countdown=30,  # hope tags are built by this time
        )

    def update_dashamail_directcrm(self) -> None:
        dashamail.push_order_event.delay(
            event_name="OrderPaid",
            order_id=self.order.pk,
        )

    def send_happiness_message(self) -> None:
        if not settings.HAPPINESS_MESSAGES_CHAT_ID:
            return

        if self.is_already_paid or self.silent or self.order.price <= 0:
            return

        send_telegram_message.delay(
            chat_id=settings.HAPPINESS_MESSAGES_CHAT_ID,
            text=self._get_happiness_message_text(self.order),
        )

    def write_success_admin_log(self) -> None:
        user = get_current_user() or self.order.user  # order may be paid anonymously, we assume customer made it

        write_admin_log.delay(
            action_flag=CHANGE,
            app="orders",
            change_message="Order paid",
            model="Order",
            object_id=self.order.id,
            user_id=user.id,
        )

    @staticmethod
    def _get_happiness_message_text(order: Order) -> str:
        sum = str(order.price).replace(".00", "")
        reason = str(order.item)
        payment_method = human_readable.get_order_payment_method_name(order)

        payment_info = f"💰+{sum} ₽, {payment_method}"

        if order.promocode:
            payment_info += f", промокод {order.promocode}"

        return f"{payment_info}\n{reason}\n{order.user}"
