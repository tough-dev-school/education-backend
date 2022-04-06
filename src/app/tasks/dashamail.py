from typing import Optional

import httpx

from app.celery import celery
from app.integrations.dashamail import AppDashamail, DashamailException


@celery.task(
    autoretry_for=[httpx.HTTPError, DashamailException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
    rate_limit='1/s',
)
def subscribe_to_dashamail(list_id: str, email: str, first_name: str, last_name: str, tags: Optional[list[str]]):
    dashamail = AppDashamail()

    dashamail.subscribe_user(
        list_id=list_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        tags=tags,
    )


@celery.task(
    autoretry_for=[httpx.HTTPError, DashamailException],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
    rate_limit='1/s',
)
def unsubscribe_from_dashamail(email: str):
    dashamail = AppDashamail()

    dashamail.unsubscribe_user(email=email)
