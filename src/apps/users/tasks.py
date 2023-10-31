import time

from django.apps import apps

from apps.users.tags.pipeline import generate_tags
from core.celery import celery
from core.tasks import update_dashamail_subscription


@celery.task(name="users.rebuild_tags")
def rebuild_tags(student_id: str | int, subscribe: bool = True) -> None:
    time.sleep(1)  # preventing race condition when task looks for user which isn't saved into db yet
    student = apps.get_model("users.Student").objects.get(pk=student_id)

    generate_tags(student)
    if subscribe:
        update_dashamail_subscription.delay(user_id=student.pk)
