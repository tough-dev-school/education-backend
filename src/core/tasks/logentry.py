from django.contrib.admin.models import LogEntry

from core.celery import celery


@celery.task
def write_admin_log(
    action_flag: int,
    change_message: str,
    content_type_id: int,
    object_id: int,
    object_repr: str,
    user_id: int,
) -> None:
    LogEntry.objects.log_action(
        action_flag=action_flag,
        change_message=change_message,
        content_type_id=content_type_id,
        object_id=object_id,
        object_repr=object_repr,
        user_id=user_id,
    )
