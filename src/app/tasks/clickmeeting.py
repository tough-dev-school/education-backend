from requests.exceptions import RequestException

from app.celery import celery
from app.integrations.clickmeeting import ClickMeetingClient, ClickMeetingHTTPException


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
