from typing import List, Union

from anymail.exceptions import AnymailRequestsAPIError
from django.apps import apps
from django.conf import settings
from requests.exceptions import RequestException

from app import tg
from app.celery import celery
from app.clickmeeting import ClickMeetingClient, ClickMeetingHTTPException
from app.mail.owl import TemplOwl
from app.mailjet import AppMailjet, AppMailjetWrongResponseException


@celery.task(
    autoretry_for=[AnymailRequestsAPIError],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def send_mail(to: Union[List, str], template_id, subject: str = '', ctx: dict = None):
    TemplOwl(
        to=to,
        template_id=template_id,
        subject=subject,
        ctx=ctx,
    ).send()


@celery.task(
    autoretry_for=[RequestException, ClickMeetingHTTPException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def invite_to_clickmeeting(room_url: str, email: str):
    client = ClickMeetingClient()
    client.invite(room_url, email)


@celery.task(
    autoretry_for=[RequestException, AppMailjetWrongResponseException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def subscribe_to_mailjet(user_id: int):
    if not all(getattr(settings, x) for x in ['MAILJET_API_KEY', 'MAILJET_SECRET_KEY', 'MAILJET_LIST_ID_ALL_CONTACTS']):
        return

    user = apps.get_model('users.User').objects.get(pk=user_id)
    mailjet = AppMailjet()

    mailjet.subscribe(user)


@celery.task
def send_happiness_message(text):
    tg.send_happiness_message(text)
