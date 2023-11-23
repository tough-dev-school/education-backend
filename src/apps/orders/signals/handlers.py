from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.stripebank.models import StripeNotification
from apps.tinkoff.models import DolyameNotification
from apps.tinkoff.models import PaymentNotification as TinkoffPaymentNotification


@receiver(post_save, sender=TinkoffPaymentNotification)
def mark_order_as_paid_on_tinkoff_bank_transactions(instance: TinkoffPaymentNotification, created: bool, **kwargs: dict[str, Any]) -> None:
    if not created:
        return

    if instance.status != "CONFIRMED":
        return

    instance.order.set_paid()


@receiver(post_save, sender=StripeNotification)
def mark_order_as_paid_on_stripe_notifications(instance: StripeNotification, created: bool, **kwargs: dict[str, Any]) -> None:
    if not created:
        return

    if instance.event_type != "checkout.session.completed":
        return

    instance.order.set_paid()  # type: ignore[union-attr]


@receiver(post_save, sender=DolyameNotification)
def mark_order_as_paid_on_dolyame_notifications(instance: DolyameNotification, created: bool, **kwargs: dict[str, Any]) -> None:
    if not created:
        return

    if instance.status != "completed":
        return

    instance.order.set_paid()
