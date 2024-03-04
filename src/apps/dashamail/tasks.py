import httpx
from django.apps import apps

from apps.dashamail import exceptions
from apps.dashamail.directcrm import events as directcrm_events
from apps.dashamail.lists.dto import DashamailSubscriber
from apps.dashamail.services import DashamailDirectCRMSubscriber
from core.celery import celery


@celery.task(
    autoretry_for=[httpx.HTTPError, exceptions.DashamailException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
    name="dashamail.update_subscription",
)
def update_subscription(student_id: int) -> None:
    user = apps.get_model("users.User").objects.get(pk=student_id)

    DashamailSubscriber(user).subscribe()


@celery.task(
    autoretry_for=[httpx.HTTPError, exceptions.DashamailDirectCRMException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
    name="dashamail.directcrm.push_order_event",
)
def push_order_event(event_name: str, order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(pk=order_id)
    Event = getattr(directcrm_events, event_name)
    Event(order).send()


@celery.task(
    autoretry_for=[httpx.HTTPError, exceptions.DashamailException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
    name="dashamail.directcrm.subscribe",
)
def directcrm_subscribe(order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(pk=order_id)

    subscriber = DashamailDirectCRMSubscriber(
        user=order.user,
        product=order.course,
    )

    subscriber()
