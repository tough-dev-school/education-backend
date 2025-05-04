from typing import Any

from django.contrib.admin.models import CHANGE, LogEntry
from django.http import HttpRequest

from apps.banking.models import CurrencyRate
from core.admin import ModelAdmin, admin
from core.tasks import write_admin_log


@admin.register(CurrencyRate)
class CurrencyRateAdmin(ModelAdmin):
    list_display = ["name", "rate"]

    def get_object(self, request: HttpRequest, object_id: str, from_field: str | None = None) -> CurrencyRate | None:
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj._original_rate = obj.rate
        return obj

    def log_change(self, request: HttpRequest, obj: CurrencyRate, message: Any) -> LogEntry:
        if obj.rate != obj._original_rate:
            return write_admin_log.delay(
                action_flag=CHANGE,
                app="banking",
                change_message=f"Currency rate was changed from {obj.__original_rate} to {obj.rate}",
                model="CurrencyRate",
                object_id=obj.id,
                user_id=request.user.id,
            )
        else:
            return super().log_change(request, obj, message)
