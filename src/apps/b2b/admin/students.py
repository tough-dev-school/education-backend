from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.b2b.models import Student
from core.admin import admin


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = [
        "name",
        "email",
    ]
    readonly_fields = [
        "name",
        "email",
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Student]:
        return super().get_queryset(request).select_related("user", "deal")

    @admin.display(description=_("name"))
    def name(self, obj: Student) -> str:
        return obj.user.get_full_name()

    @admin.display(description=_("email"))
    def email(self, obj: Student) -> str:
        return obj.user.email

    def has_add_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    def has_change_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: Any, obj: Any = None) -> bool:
        """Block student deletion for complete and canceled deals"""
        if obj is None:
            return super().has_delete_permission(request, obj)

        return obj.canceled is None and obj.completed is None

    class Media:
        css = {
            "all": ("admin/css/condensed_students.css",),
        }
