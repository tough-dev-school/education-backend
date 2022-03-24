import contextlib
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from stripebank.models import StripeNotification
from tinkoff.models import CreditNotification as TinkoffCreditNotification
from tinkoff.models import PaymentNotification as TinkoffPaymentNotification


@receiver(post_save, sender=TinkoffPaymentNotification)
def mark_order_as_paid_on_tinkoff_bank_transactions(instance: TinkoffPaymentNotification, created: bool, **kwargs):
    if not created:
        return

    if instance.status != 'CONFIRMED':
        return

    order = Order.objects.get(pk=instance.order_id)
    order.set_paid()


@receiver(post_save, sender=TinkoffCreditNotification)
def mark_order_as_paid_on_tinkoff_credit_transactions(instance: TinkoffCreditNotification, created: bool, **kwargs):
    if not created:
        return

    if instance.status != 'signed':
        return

    order = Order.objects.get(pk=instance.order_id)
    order.set_paid()


@receiver(post_save, sender=StripeNotification)
def mark_order_as_paid_on_stripe_notifications(instance: StripeNotification, created: bool, **kwargs):
    if not created:
        return

    if instance.status != 'complete':
        return

    if 'tds-' not in instance.order_id:
        return

    with contextlib.suppress(Order.DoesNotExist):
        order = Order.objects.get(pk=instance.order_id.replace('tds-', ''))
        order.set_paid()
