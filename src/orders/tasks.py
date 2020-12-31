from app.celery import celery
from orders.models import Order


@celery.task
def ship_order(order_id: int, **kwargs):
    Order.objects.get(pk=order_id).ship(**kwargs)


@celery.task
def ship_unshipped_orders():
    for order in Order.objects.to_ship():
        ship_order.delay(order.pk, silent=True)
