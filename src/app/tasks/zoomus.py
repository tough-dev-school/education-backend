from django.apps import apps
from requests.exceptions import RequestException

from app.celery import celery
from app.integrations.zoomus import ZoomusClient, ZoomusHTTPException


@celery.task(
    autoretry_for=[RequestException, ZoomusHTTPException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def invite_to_zoomus(webinar_id: str, user_id: int):
    user = apps.get_model('users.User').objects.get(pk=user_id)

    client = ZoomusClient()
    client.invite(webinar_id, user)
