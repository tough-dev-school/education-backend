from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from homework import tasks
from homework.models import Answer


@receiver(post_save, sender=Answer)
def send_new_answer_notification(instance, created, **kwargs):
    if settings.DISABLE_NEW_ANSWER_NOTIFICATIONS:
        return

    if not created:
        return

    tasks.notify_about_new_answer.apply_async(
        countdown=60,
        kwargs={
            'answer_id': instance.pk,
        },
    )
