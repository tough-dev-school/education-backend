import time

from django.apps import apps

from app.celery import celery
from app.tasks import update_dashamail_subscription
from users.tags.pipeline import generate_tags


@celery.task(name="users.rebuild_tags")
def rebuild_tags(student_id: str | int, list_id: str | None = None) -> None:
    time.sleep(1)  # preventing race condition when task looks for user which isn't saved into db yet
    student = apps.get_model("users.Student").objects.get(pk=student_id)

    generate_tags(student)
    update_dashamail_subscription.delay(user_id=student.pk, list_id=list_id)
