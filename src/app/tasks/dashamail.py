import httpx

from django.apps import apps

from app.celery import celery
from app.integrations.dashamail import DashamailException
from app.integrations.dashamail.subscription_updater import SubscriptionUpdater


@celery.task(
    autoretry_for=[httpx.HTTPError, DashamailException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
)
def update_dashamail_subscription(user_id: int, list_id: str | None = None) -> None:
    user = apps.get_model("users.User").objects.filter(pk=user_id).first()

    if user is not None:
        SubscriptionUpdater(user, list_id)()
