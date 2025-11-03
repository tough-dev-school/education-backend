from apps.b2b.models import Customer
from core.admin import ModelAdmin, admin


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    fields = ["name", "tin"]
    list_display = [
        "tin",
        "name",
    ]
    search_fields = [
        "tin",
        "name",
    ]
    list_display_links = [
        "tin",
        "name",
    ]
    actions = [
        "delete_selected",
    ]


__all__ = [
    "CustomerAdmin",
]
