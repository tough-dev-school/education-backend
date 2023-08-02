from httpx import TransportError

from django.apps import apps
from django.conf import settings

from amocrm.client import AmoCRMClient
from amocrm.client.http import AmoCRMClientException
from amocrm.models import AmoCRMUser
from amocrm.services.access_token_getter import AmoCRMTokenGetterException
from amocrm.services.course_creator import AmoCRMCourseCreator
from amocrm.services.course_updater import AmoCRMCourseUpdater
from amocrm.services.product_groups_updater import AmoCRMProductGroupsUpdater
from app.celery import celery


def amocrm_enabled() -> bool:
    return settings.AMOCRM_BASE_URL != ""


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def enable_customers() -> None:
    client = AmoCRMClient()
    client.enable_customers()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def push_customer(user_id: int) -> None:
    client = AmoCRMClient()
    user = apps.get_model("users.User").objects.get(id=user_id)
    if hasattr(user, "amocrm_user"):
        client.update_customer(amocrm_user=user.amocrm_user)
    else:
        amocrm_id = client.create_customer(user=user)
        AmoCRMUser.objects.create(user=user, amocrm_id=amocrm_id)


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def push_product_groups() -> None:
    AmoCRMProductGroupsUpdater()()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def push_course(course_id: int) -> None:
    course = apps.get_model("products.Course").objects.get(id=course_id)
    if hasattr(course, "amocrm_course"):
        AmoCRMCourseUpdater(amocrm_course=course.amocrm_course)()
    else:
        AmoCRMCourseCreator(course=course)()
