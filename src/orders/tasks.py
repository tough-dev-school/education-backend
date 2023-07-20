from app.celery import celery
from orders.models import Order


@celery.task
def generate_diploma(order_id: int) -> None:
    from orders.services import OrderDiplomaGenerator

    order = Order.objects.get(pk=order_id)

    OrderDiplomaGenerator(order)()
