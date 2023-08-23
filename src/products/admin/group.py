from typing import Any

from django.http import HttpRequest

from amocrm import tasks
from app.admin import admin
from app.admin import ModelAdmin
from products.models import Group


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ["id", "name", "slug"]
    list_editable = ["name", "slug"]

    def save_model(self, request: HttpRequest, obj: Group, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)

        if tasks.amocrm_enabled():
            tasks.push_product_groups.apply_async(countdown=1)
