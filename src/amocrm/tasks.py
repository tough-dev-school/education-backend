from httpx import TransportError

from django.conf import settings

from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMUser
from app.celery import celery
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


@celery.task
def update_customer(amocrm_user_id: int) -> int:
    client = AmoCRMClient()
    amocrm_user = AmoCRMUser.objects.get(amocrm_id=amocrm_user_id)
    return client.update_customer(amocrm_user=amocrm_user)
