import httpx

from django.apps import apps

from apps.dashamail.exceptions import DashamailException
from apps.dashamail.lists.client import DashamailListsClient
from core.celery import celery


@celery.task(
    autoretry_for=[httpx.HTTPError, DashamailException],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    rate_limit="1/s",
    name="dashamail.update_subscription",
)
def update_dashamail_subscription(student_id: int) -> None:
    user = apps.get_model("users.User").objects.get(pk=student_id)

    DashamailListsClient().subscribe_or_update(user)
