import httpx

from app.celery import celery
from banking.atol import AtolClient
from orders.models import Order


@celery.task(
    autoretry_for=[httpx.HTTPError],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
    acks_late=True,
)
def print_atol_receipt(order_id: int) -> None:
    atol = AtolClient(order=Order.objects.get(pk=order_id))

    atol()
