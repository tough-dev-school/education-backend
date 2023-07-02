from rest_framework.request import Request

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin


@admin.action(description=_("Deactivate selected promo codes"))
def deactivate(modeladmin: ModelAdmin, request: Request, queryset: QuerySet) -> None:
    queryset.update(active=False)
