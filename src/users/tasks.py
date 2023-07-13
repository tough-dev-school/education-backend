from django.apps import apps

from app.celery import celery
from app.tasks import update_dashamail_subscription
from users.tags.pipeline import apply_tags


@celery.task()
def rebuild_tags(student_id: str | int, list_id: str | None = None) -> None:
    student = apps.get_model("users.Student").objects.get(pk=student_id)

    apply_tags(student)
    update_dashamail_subscription.delay(user_id=student.pk, list_id=list_id)
