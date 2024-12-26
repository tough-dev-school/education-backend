from typing import Any

from django.contrib.admin.models import CHANGE, LogEntry
from django.http import HttpRequest

from apps.banking.models import Acquiring
from core.admin import ModelAdmin, admin
from core.tasks import write_admin_log


@admin.register(Acquiring)
class AcquiringAdmin(ModelAdmin):
    list_display = ["bank", "percent"]

    def get_object(self, request: HttpRequest, object_id: str, from_field: str | None = None) -> Acquiring | None:
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj.__original_percent = obj.percent
        return obj

    def log_change(self, request: HttpRequest, obj: Acquiring, message: Any) -> LogEntry:
        if obj.percent != obj.__original_percent:  # type: ignore[attr-defined]
            return write_admin_log(
                action_flag=CHANGE,
                app="banking",
                change_message=f"Aquiring percent was changed from {obj.__original_percent} to {obj.percent}",  # type: ignore[attr-defined]
                model="Acquiring",
                object_id=obj.id,
                user_id=request.user.id,
            )
        else:
            return super().log_change(request, obj, message)
