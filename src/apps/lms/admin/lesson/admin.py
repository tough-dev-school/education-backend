from typing import no_type_check

from django.apps import apps
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.lms.admin.lesson import filters
from apps.lms.admin.lesson.form import LessonForm
from apps.lms.models import Lesson
from core.admin import ModelAdmin, admin


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    form = LessonForm
    list_filter = [
        filters.LessonArchivedFilter,
        filters.LessonCourseFilter,
    ]
    fields = [
        "material",
        "question",
        "call",
        "hidden",
        "material_id",
        "material_title",
    ]
    readonly_fields = [
        "course_name",
        "module_name",
        "material_id",
        "material_title",
        "question_name",
    ]
    foreignkey_queryset_overrides = {
        "lms.Lesson.question": lambda apps: apps.get_model("homework.Question").objects.filter(archived=False).distinct(),
    }

    list_display = [
        "id",
        "course_name",
        "module_name",
        "material_title",
        "question_name",
    ]

    list_display_links = [
        "id",
        "course_name",
    ]

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/add_material_link.js", "admin/remove_call_select.js"]
        css = {
            "all": ["admin/lesson_form.css"],
        }

    def has_change_permission(self, request: HttpRequest, lesson: Lesson | None = None) -> bool:
        """Disallow editing archived lessons"""
        if lesson is None:
            return True

        return not lesson.is_archived()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Lesson]:
        return super().get_queryset(request).for_admin()  # type: ignore

    @no_type_check
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Custom querysets for ForeignKey fields. Works in the add form only to prevent losing data during edit"""
        if hasattr(self, "foreignkey_queryset_overrides") and str(db_field) in self.foreignkey_queryset_overrides:
            kwargs["queryset"] = self.foreignkey_queryset_overrides[str(db_field)](apps)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description=_("Material"))
    def material_id(self, lesson: Lesson) -> int | None:
        return lesson.material_id

    @admin.display(description=_("Course"), ordering="module__course__name")
    def course_name(self, lesson: Lesson) -> str:
        return lesson.module.course.name

    @admin.display(description=_("Module"), ordering="module__name")
    def module_name(self, lesson: Lesson) -> str:
        return lesson.module.name

    @admin.display(description=_("Material"), ordering="material__title")
    def material_title(self, lesson: Lesson) -> str:
        if lesson.material is not None:
            return lesson.material.title

        return "—"

    @admin.display(description=_("Question"), ordering="question__name")
    def question_name(self, lesson: Lesson) -> str:
        if lesson.question is not None:
            return lesson.question.name

        return "—"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


__all__ = [
    "LessonAdmin",
]
