from rest_framework.request import Request

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from app.admin.filters import BooleanFilter


class IsRootFilter(BooleanFilter):
    title = _("Is root answer")
    parameter_name = "is_root"

    def t(self, request: Request, queryset: QuerySet) -> QuerySet:
        return queryset.filter(parent__isnull=True)

    def f(self, request: Request, queryset: QuerySet) -> QuerySet:
        return queryset.filter(parent__isnull=False)
