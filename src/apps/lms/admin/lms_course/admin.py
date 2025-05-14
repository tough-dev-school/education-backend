from typing import Any

from adminsortable2.admin import SortableAdminBase
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.lms.admin.module.inline import ModuleInline
from apps.lms.models import Course
from core.admin import ModelAdmin, admin


@admin.register(Course)
class CourseAdmin(SortableAdminBase, ModelAdmin):
    fieldsets = [
        (
            _("Name"),
            {
                "fields": [
                    "name",
                    "cover",
                ],
            },
        ),
        (
            _("URLs"),
            {
                "fields": [
                    "calendar_google",
                    "calendar_ios",
                    "chat",
                ],
            },
        ),
    ]
    readonly_fields = [
        "name",
        "module_count",
    ]
    list_display = [
        "name",
        "module_count",
    ]
    list_filter = [
        "group",
    ]

    inlines = [ModuleInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Course]:
        return super().get_queryset(request).for_admin()  # type: ignore

    @admin.display(description=_("Module count"), ordering="module_count")
    def module_count(self, obj: Course) -> str:
        if not obj.module_count:
            return "—"

        return str(obj.module_count)

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    class Media:
        css = {
            "all": ("admin/condensed_lms_sortables.css",),
        }
