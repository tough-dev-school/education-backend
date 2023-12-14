from typing import TYPE_CHECKING

from django.contrib.admin.models import LogEntry

from core.celery import celery

if TYPE_CHECKING:
    from typing import Any


@celery.task
def write_admin_log(**kwargs: "Any") -> None:
    LogEntry.objects.log_action(**kwargs)
