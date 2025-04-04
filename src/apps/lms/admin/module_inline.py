from adminsortable2.admin import SortableTabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.lms.models import Module
from core.admin import admin


class ModuleInline(SortableTabularInline):
    model = Module
    fields = [
        "_name",
        "hidden",
    ]
    readonly_fields = [
        "_name",
    ]
    extra = 0

    @mark_safe
    @admin.display(description=_("Name"))
    def _name(self, lesson: Module) -> str:
        lesson_url = reverse("admin:lms_module_change", args=[lesson.id])
        return f"<a href='{lesson_url}'>{lesson.name}</a>"
