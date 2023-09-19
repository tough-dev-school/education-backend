from functools import partial
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

from homework import tasks
from homework.models import Answer


@receiver(post_save, sender=Answer)
def send_new_answer_notification(instance: Model, created: Any, **kwargs: dict[str, Any]) -> None:
    if settings.DISABLE_NEW_ANSWER_NOTIFICATIONS:
        return

    if not created:
        return

    transaction.on_commit(partial(tasks.notify_about_new_answer.delay, answer_id=instance.pk))
