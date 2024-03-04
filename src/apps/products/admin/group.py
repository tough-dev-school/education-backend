from typing import Any

from django.http import HttpRequest

from apps.amocrm import tasks
from apps.products.models import Group
from core.admin import ModelAdmin, admin


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ["id", "name", "slug"]
    list_editable = ["name", "slug"]

    fields = [
        "name",
        "slug",
    ]

    def save_model(self, request: HttpRequest, obj: Group, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)

        if tasks.amocrm_enabled():
            tasks.push_product_groups.apply_async(countdown=1)
