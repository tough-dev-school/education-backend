import httpx

from app.celery import celery
from orders.models import Order
from tinkoff.dolyame import Dolyame
from tinkoff.dolyame import DolyameRequestException


@celery.task(
    acks_late=True,
    autoretry_for=[DolyameRequestException, httpx.HTTPError],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
)
def commit_dolyame_order(order_id: int, idempotency_key: str) -> None:
    dolyame = Dolyame(
        order=Order.objects.get(pk=order_id),
        idempotency_key=idempotency_key,
    )

    dolyame.commit()


@celery.task(
    acks_late=True,
    autoretry_for=[DolyameRequestException, httpx.HTTPError],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
)
def refund_dolyame_order(order_id: int, idempotency_key: str) -> None:
    dolyame = Dolyame(
        order=Order.objects.get(pk=order_id),
        idempotency_key=idempotency_key,
    )

    dolyame.refund()
