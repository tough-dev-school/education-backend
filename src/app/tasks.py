from typing import List, Union

from anymail.exceptions import AnymailRequestsAPIError
from requests.exceptions import RequestException

from app.celery import celery
from app.clickmeeting import ClickMeetingClient, ClickMeetingHTTPException
from app.mail.owl import TemplOwl


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
