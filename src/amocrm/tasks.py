import time

from celery import chain
from celery import Task
from httpx import TransportError

from django.apps import apps
from django.conf import settings

from amocrm.client import AmoCRMClient
from amocrm.client.http import AmoCRMClientException
from amocrm.services.access_token_getter import AmoCRMTokenGetterException
from amocrm.services.orders.order_pusher import AmoCRMOrderPusher
from amocrm.services.orders.order_returner import AmoCRMOrderReturner
from amocrm.services.products.course_creator import AmoCRMCourseCreator
from amocrm.services.products.course_updater import AmoCRMCourseUpdater
from amocrm.services.products.product_groups_updater import AmoCRMProductGroupsUpdater
from amocrm.services.user_pusher import AmoCRMUserPusher
from app.celery import celery

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
    time.sleep(1)  # avoid race condition when user is not saved yet
    user = apps.get_model("users.User").objects.get(id=user_id)
    AmoCRMUserPusher(user=user)()


@celery.task(base=AmoTask)
def push_order(order_id: int) -> None:
    time.sleep(3)  # avoid race condition when order is not saved yet
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    AmoCRMOrderPusher(order=order)()


@celery.task(base=AmoTask)
def return_order(order_id: int) -> None:
    order = apps.get_model("orders.Order").objects.get(id=order_id)
    AmoCRMOrderReturner(order=order)()


@celery.task(base=AmoTask)
def push_product_groups() -> None:
    AmoCRMProductGroupsUpdater()()


@celery.task(base=AmoTask)
def push_course(course_id: int) -> int:
    course = apps.get_model("products.Course").objects.get(id=course_id)
    if hasattr(course, "amocrm_course"):
        return AmoCRMCourseUpdater(amocrm_course=course.amocrm_course)()
    else:
        return AmoCRMCourseCreator(course=course)()


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
