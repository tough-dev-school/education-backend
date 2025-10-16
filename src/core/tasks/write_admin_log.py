from django.apps import apps
from django.contrib.admin.models import LogEntry

from core.celery import celery


@celery.task
def write_admin_log(action_flag: int, change_message: str, model: str, object_id: int, user_id: int) -> LogEntry:
    Model = apps.get_model(model)

    return LogEntry.objects.log_actions(
        action_flag=action_flag,
        change_message=change_message,
        queryset=Model.objects.filter(pk=object_id),
        user_id=user_id,
    )


__all__ = [
    "write_admin_log",
]
