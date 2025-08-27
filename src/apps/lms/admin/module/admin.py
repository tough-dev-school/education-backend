from adminsortable2.admin import SortableAdminBase
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.lms.admin.lesson.inline import LessonInline
from apps.lms.admin.module import actions
from apps.lms.models import Module
from apps.products.admin.filters import CourseFilter
from core.admin import ModelAdmin, admin
from core.admin.filters import DefaultFalseBooleanFilter


class Archived(DefaultFalseBooleanFilter):
    title = _("Archived")
    parameter_name = "archived"

    def t(self, request: HttpRequest, queryset: QuerySet[Module]) -> QuerySet:
        return queryset.filter(archived=True)

    def f(self, request: HttpRequest, queryset: QuerySet[Module]) -> QuerySet:
        return queryset.filter(archived=False)


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
        Archived,
        CourseFilter,
    ]

    inlines = [
        LessonInline,
    ]
    actions = [
        actions.archive,
        actions.unarchive,
    ]

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/autoset-hidden-fiend-during-lesson-adding.js"]

    foreignkey_queryset_overrides = {
        "lms.Module.course": lambda apps: apps.get_model("lms.Course").objects.for_admin(),
    }

    def get_queryset(self, request: HttpRequest) -> QuerySet[Module]:
        return super().get_queryset(request).for_admin()  # type: ignore

    @admin.display(description=_("Lesson count"), ordering="lesson_count")
    def lesson_count(self, obj: Module) -> str:
        if not obj.lesson_count:
            return "—"

        return str(obj.lesson_count)


__all__ = [
    "Module",
]
