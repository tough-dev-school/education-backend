from django.apps import apps
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from core.celery import celery


@celery.task
def write_admin_log(
    action_flag: int,
    app: str,
    change_message: str,
    model: str,
    object_id: int,
    object_repr: str,
    user_id: int,
) -> None:
    model = apps.get_model(app, model)  # type: ignore[assignment]

    content_type_id = ContentType.objects.get_for_model(model).id  # type: ignore[arg-type]

    LogEntry.objects.log_action(
        action_flag=action_flag,
        change_message=change_message,
        content_type_id=content_type_id,
        object_id=object_id,
        object_repr=object_repr,
        user_id=user_id,
    )
