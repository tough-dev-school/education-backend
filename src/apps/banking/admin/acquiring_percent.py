from apps.banking.models import AcquiringPercent
from core.admin import ModelAdmin, admin


@admin.register(AcquiringPercent)
class AcquiringPercentAdmin(ModelAdmin):
    fields = [
        "slug",
        "percent",
    ]

    list_display = [
        "slug",
        "percent",
    ]

    list_editable = ["percent"]
