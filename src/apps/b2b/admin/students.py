from typing import Any

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

    def name(self, obj: Student) -> str:
        return obj.user.get_full_name()

    def email(self, obj: Student) -> str:
        return obj.user.email

    def has_add_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    def has_change_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    class Media:
        css = {
            "all": ("admin/css/condensed_students.css",),
        }
