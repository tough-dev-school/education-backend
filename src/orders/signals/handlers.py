from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from tinkoff.models import PaymentNotification as TinkoffPaymentNotification


@receiver(post_save, sender=TinkoffPaymentNotification)
def mark_order_as_payd_on_tinkoff_transactions(instance, created, **kwargs):
    if not created:
        return

    if instance.status != 'CONFIRMED':
        return

    order = Order.objects.get(pk=instance.order_id)
    order.set_paid()
