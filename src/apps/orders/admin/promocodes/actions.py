from typing import Any

from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from core.admin import admin


@admin.action(description=_("Deactivate selected promo codes"))
def deactivate(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(active=False)
