from apps.lms.models import Call
from core.admin import ModelAdmin, admin


@admin.register(Call)
class CallAdmin(ModelAdmin):
    fields = [
        "name",
        "url",
    ]


__all__ = ["CallAdmin"]
