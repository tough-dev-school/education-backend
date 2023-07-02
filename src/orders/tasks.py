from typing import Any

from app.celery import celery
from orders.models import Order


@celery.task
def ship_order(order_id: int, **kwargs: dict[str, Any]) -> None:
    Order.objects.get(pk=order_id).ship(**kwargs)  # type: ignore


@celery.task
def ship_unshipped_orders() -> None:
    for order in Order.objects.to_ship():
        ship_order.delay(order.pk, silent=True)


@celery.task
def generate_diploma(order_id: int) -> None:
    from orders.services import OrderDiplomaGenerator

    order = Order.objects.get(pk=order_id)

    OrderDiplomaGenerator(order)()
