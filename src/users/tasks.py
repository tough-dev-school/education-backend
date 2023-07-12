from django.apps import apps

from app.celery import celery
from users.tags.tags_synchronizer import TagsSynchronizer


@celery.task()
def rebuild_tags(student_id: str | int, list_id: str | None = None) -> None:
    student = apps.get_model("users.Student").objects.get(pk=student_id)
    TagsSynchronizer(student=student, list_id=list_id)()
