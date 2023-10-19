from apps.orders.models import Order
from core.celery import celery


@celery.task
def generate_diploma(order_id: int) -> None:
    from apps.orders.services import OrderDiplomaGenerator

    order = Order.objects.get(pk=order_id)

    OrderDiplomaGenerator(order)()
