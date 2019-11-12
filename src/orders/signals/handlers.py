from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.tasks import send_happiness_message
from orders.models import Order
from orders.signals import order_got_shipped
from tinkoff.models import PaymentNotification as TinkoffPaymentNotification


@receiver(post_save, sender=TinkoffPaymentNotification)
def mark_order_as_payd_on_tinkoff_transactions(instance, created, **kwargs):
    if not created:
        return

    if instance.status != 'CONFIRMED':
        return

    order = Order.objects.get(pk=instance.order_id)
    order.set_paid()


@receiver(order_got_shipped)
def notify_tg_when_order_is_shipped(order, **kwargs):
    if not settings.SEND_HAPPINESS_MESSAGES:
        return

    send_happiness_message.delay(text='💰+{sum} ₽, {user}, {reason}'.format(
        sum=str(order.price).replace('.00', ''),
        user=str(order.user),
        reason=str(order.item),
    ))
