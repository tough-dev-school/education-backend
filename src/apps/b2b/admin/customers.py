from apps.b2b.models import Customer
from core.admin import ModelAdmin, admin


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    fields = ["name"]
    list_display = [
        "name",
    ]
    actions = [
        "delete_selected",
    ]


__all__ = [
    "CustomerAdmin",
]
