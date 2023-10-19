from celery import Task
from httpx import TransportError

from django.apps import apps
from django.conf import settings

from apps.amocrm.client import AmoCRMClient
from apps.amocrm.client.http import AmoCRMClientException
from apps.amocrm.services.access_token_getter import AmoCRMTokenGetterException
from apps.amocrm.services.course_pusher import AmoCRMCoursePusher
from apps.amocrm.services.group_pusher import AmoCRMGroupsPusher
from apps.amocrm.services.orders.order_pusher import AmoCRMOrderPusher
from apps.amocrm.services.orders.order_returner import AmoCRMOrderReturner
from apps.amocrm.services.user_pusher import AmoCRMUserPusher
from core.celery import celery

__all__ = [
    "amocrm_enabled",
    "push_user",
    "push_order",
    "return_order",
    "push_product_groups",
    "push_course",
    "push_all_products_and_product_groups",
]


class AmoTask(Task):
    autoretry_for = [TransportError, AmoCRMTokenGetterException, AmoCRMClientException]
    retry_kwargs = {
        "max_retries": 10,
        "countdown": 1,
    }
    rate_limit = "3/s"
    acks_late = True


def amocrm_enabled() -> bool:
    return settings.AMOCRM_BASE_URL != ""


@celery.task(base=AmoTask)
def push_user(user_id: int) -> None:
    user = apps.get_model("users.User").objects.get(id=user_id)
    AmoCRMUserPusher(user=user)()


@celery.task(base=AmoTask)
def push_order(order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    AmoCRMOrderPusher(order=order)()


@celery.task(base=AmoTask)
def return_order(order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    AmoCRMOrderReturner(order=order)()


@celery.task(base=AmoTask)
def push_product_groups() -> None:
    AmoCRMGroupsPusher()()


@celery.task(base=AmoTask)
def push_course(course_id: int) -> None:
    course = apps.get_model("products.Course").objects.get(id=course_id)
    AmoCRMCoursePusher(course=course)()


@celery.task(base=AmoTask)
def push_all_products_and_product_groups() -> None:
    push_product_groups.apply_async(link=_push_all_courses.si())


@celery.task(base=AmoTask)
def enable_customers() -> None:
    client = AmoCRMClient()
    client.enable_customers()


@celery.task(base=AmoTask)
def _push_all_courses() -> None:
    courses = apps.get_model("products.Course").objects.all()
    for course in courses:
        push_course.delay(course_id=course.id)
