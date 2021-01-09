from typing import List, Union

from anymail.exceptions import AnymailRequestsAPIError
from django.apps import apps
from django.conf import settings
from requests.exceptions import RequestException

from app.celery import celery
from app.integrations import tg
from app.integrations.clickmeeting import ClickMeetingClient, ClickMeetingHTTPException
from app.integrations.mailchimp import AppMailchimp, MailchimpHTTPException
from app.integrations.mailjet import AppMailjet, AppMailjetWrongResponseException
from app.integrations.zoomus import ZoomusClient, ZoomusHTTPException
from app.mail.owl import TemplOwl


@celery.task(
    autoretry_for=[AnymailRequestsAPIError],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def send_mail(to: Union[List, str], template_id, subject: str = '', ctx: dict = None, disable_antispam=False):
    TemplOwl(
        to=to,
        template_id=template_id,
        subject=subject,
        ctx=ctx,
        disable_antispam=disable_antispam,
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


@celery.task(
    autoretry_for=[RequestException, AppMailjetWrongResponseException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def subscribe_to_mailjet(user_id: int):
    if not all(getattr(settings, x) for x in ['MAILJET_API_KEY', 'MAILJET_SECRET_KEY', 'MAILJET_CONTACT_LIST_ID']):
        return

    user = apps.get_model('users.User').objects.get(pk=user_id)
    mailjet = AppMailjet()

    mailjet.subscribe(user)


@celery.task(
    autoretry_for=[RequestException, MailchimpHTTPException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def subscribe_to_mailchimp(user_id: int, list_id=None):
    if list_id is None:
        list_id = settings.MAILCHIMP_CONTACT_LIST_ID

    if not list_id:
        return

    mailchimp = AppMailchimp()

    mailchimp.subscribe_django_user(
        list_id=list_id,
        user=apps.get_model('users.User').objects.get(pk=user_id),
    )


@celery.task
def send_happiness_message(text):
    tg.send_happiness_message(text)
