from httpx import TransportError

from django.conf import settings

from amocrm.client import AmoCRMClient
from amocrm.client.http import AmoCRMClientException
from amocrm.models import AmoCRMCourse
from amocrm.models import AmoCRMUser
from amocrm.services.access_token_getter import AmoCRMTokenGetterException
from amocrm.services.course_creator import AmoCRMCourseCreator
from amocrm.services.course_updater import AmoCRMCourseUpdater
from amocrm.services.product_groups_updater import AmoCRMProductGroupsUpdater
from app.celery import celery
from products.models import Course
from users.models import User


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
def create_customer(user_id: int) -> int:
    client = AmoCRMClient()
    user = User.objects.get(id=user_id)
    return client.create_customer(user=user)


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def update_customer(amocrm_user_id: int) -> int:
    client = AmoCRMClient()
    amocrm_user = AmoCRMUser.objects.get(amocrm_id=amocrm_user_id)
    return client.update_customer(amocrm_user=amocrm_user)


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def update_product_groups() -> None:
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
def create_course(course_id: int) -> None:
    course = Course.objects.get(id=course_id)
    AmoCRMCourseCreator(course)()


@celery.task(
    autoretry_for=[TransportError, AmoCRMTokenGetterException, AmoCRMClientException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 1,
    },
    rate_limit="3/s",
    acks_late=True,
)
def update_course(amocrm_course_id: int) -> None:
    amocrm_course = AmoCRMCourse.objects.get(id=amocrm_course_id)
    AmoCRMCourseUpdater(amocrm_course)()
