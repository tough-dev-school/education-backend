from httpx import TransportError

from amocrm.client import AmoCRMClient
from amocrm.client.http import AmoCRMClientException
from amocrm.models import AmoCRMUser
from amocrm.services.access_token_getter import AmoCRMTokenGetterException
from app.celery import celery
from users.models import User

client = AmoCRMClient()


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
    amocrm_user = AmoCRMUser.objects.get(amocrm_id=amocrm_user_id)
    return client.update_customer(amocrm_user=amocrm_user)
