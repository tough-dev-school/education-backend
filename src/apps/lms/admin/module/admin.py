from adminsortable2.admin import SortableAdminBase
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.lms.admin.lesson.inline import LessonInline
from apps.lms.models import AnnotatedModule, Module
from apps.products.admin.filters import CourseFilter
from core.admin import ModelAdmin, admin
from core.admin.actions import archive
from core.admin.filters import ArchivedFilter


@admin.register(Module)
class ModuleAdmin(SortableAdminBase, ModelAdmin):
    fields = [
        "name",
        "start_date",
        "course",
        "archived",
        "description",
        "text",
    ]
    readonly_fields = [
        "lesson_count",
    ]
    list_display = [
        "course",
        "name",
        "lesson_count",
    ]
    list_filter = [
        ArchivedFilter,
        CourseFilter,
    ]

    inlines = [
        LessonInline,
    ]
    actions = [
        archive.archive,
        archive.unarchive,
    ]

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/autoset-hidden-fiend-during-lesson-adding.js"]

    foreignkey_queryset_overrides = {
        "lms.Module.course": lambda apps: apps.get_model("lms.Course").objects.for_admin(),
    }

    def get_queryset(self, request: HttpRequest) -> QuerySet[Module]:
        return super().get_queryset(request).for_admin()  # type: ignore

    @admin.display(description=_("Lesson count"), ordering="lesson_count")
    def lesson_count(self, obj: AnnotatedModule) -> str:
        if not obj.lesson_count:  # type: ignore[attr-defined]
            return "—"

        return str(obj.lesson_count)  # type: ignore[attr-defined]


__all__ = [
    "Module",
]
