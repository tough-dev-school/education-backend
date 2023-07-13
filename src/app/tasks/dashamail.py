import httpx

from app.celery import celery
from app.integrations.dashamail import AppDashamail
from app.integrations.dashamail import DashamailException


@celery.task(
    autoretry_for=[httpx.HTTPError, DashamailException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
)
def manage_subscription_to_dashamail(list_id: str, email: str, first_name: str, last_name: str, tags: list[str]) -> None:
    dashamail = AppDashamail()

    member_id, is_active = dashamail.get_subscriber(list_id=list_id, email=email)

    if member_id is None:
        dashamail.subscribe_user(
            list_id=list_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            tags=tags,
        )
    else:
        dashamail.update_subscriber(
            list_id=list_id,
            member_id=member_id,
            first_name=first_name,
            last_name=last_name,
            tags=tags,
        )
