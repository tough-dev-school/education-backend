from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import RequestException

from app.celery import celery
from app.integrations.dashamail import AppDashamail, DashamailException


@celery.task(
    autoretry_for=[RequestException, DashamailException, ObjectDoesNotExist],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
    rate_limit='1/s',
)
def subscribe_to_dashamail(user_id: int, list_id=None, tags=None):
    if list_id is None:
        list_id = settings.DASHAMAIL_LIST_ID

    if not list_id:
        return

    dashamail = AppDashamail()

    dashamail.subscribe_django_user(
        list_id=list_id,
        user=apps.get_model('users.User').objects.get(pk=user_id),
        tags=tags,
    )


@celery.task(
    autoretry_for=[RequestException, DashamailException, ObjectDoesNotExist],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
    rate_limit='1/s',
)
def unsubscribe_from_dashamail(user_id: int, list_id=None):
    if list_id is None:
        list_id = settings.DASHAMAIL_LIST_ID

    if not list_id:
        return

    dashamail = AppDashamail()

    dashamail.unsubscribe_django_user(
        list_id=list_id,
        user=apps.get_model('users.User').objects.get(pk=user_id),
    )
