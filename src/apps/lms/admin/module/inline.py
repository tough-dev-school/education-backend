from adminsortable2.admin import SortableTabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.lms.models import Module
from core.admin import admin


class ModuleInline(SortableTabularInline):
    model = Module
    fields = [
        "name",
        "_edit",
        "hidden",
    ]
    readonly_fields = [
        "_edit",
    ]
    extra = 0

    @mark_safe
    @admin.display(description=_("Name"))
    def _edit(self, lesson: Module) -> str:
        if lesson.id is None:
            return "—"  # type: ignore

        lesson_url = reverse("admin:lms_module_change", args=[lesson.id])
        return f"<a href='{lesson_url}'>Редактировать</a>"
