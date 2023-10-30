import httpx

from django.apps import apps

from core.celery import celery
from core.integrations.dashamail import DashamailException
from core.integrations.dashamail.subscription_updater import SubscriptionUpdater


@celery.task(
    autoretry_for=[httpx.HTTPError, DashamailException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
    name="dashamail.update_subscription",
)
def update_dashamail_subscription(user_id: int) -> None:
    user = apps.get_model("users.User").objects.get(pk=user_id)

    SubscriptionUpdater(user)()
