from adminsortable2.admin import SortableAdminBase, SortableTabularInline
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.lms.models import Lesson, LessonCourse
from core.admin import ModelAdmin, admin


class LessonInline(SortableTabularInline):
    model = Lesson
    fields = [
        "_name",
        "_material",
        "_question",
        "hidden",
    ]
    readonly_fields = [
        "_name",
        "_material",
        "_question",
    ]
    extra = 0

    @mark_safe
    @admin.display(description=_("Name"))
    def _name(self, lesson: Lesson) -> str:
        lesson_url = reverse("admin:lms_lesson_change", args=[lesson.id])
        return f"<a href='{lesson_url}'>{lesson.name}</a>"

    @mark_safe
    @admin.display(description=_("Homework"))
    def _question(self, lesson: Lesson) -> str:
        if lesson.question is not None:
            question_url = reverse("admin:homework_question_change", args=[lesson.question_id])
            return f"<a href='{question_url}'>смотреть</a>"
        else:
            return "—"

    @mark_safe
    @admin.display(description=pgettext_lazy("lessons", "Material"))
    def _material(self, lesson: Lesson) -> str:
        if lesson.material_id is not None:
            material_url = reverse("admin:notion_material_change", args=[lesson.material_id])
            return f"<a href='{material_url}'>смотреть</a>"
        else:
            return "—"


@admin.register(LessonCourse)
class LessonCourseAdmin(SortableAdminBase, ModelAdmin):
    fields = [
        "name",
    ]
    readonly_fields = [
        "name",
        "lesson_count",
    ]
    list_display = [
        "name",
        "lesson_count",
    ]
    list_filter = [
        "group",
    ]

    inlines = [LessonInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).for_admin()  # type: ignore

    @admin.display(description=("Lesson count"), ordering="lesson_count")
    def lesson_count(self, obj: LessonCourse) -> str:
        if not obj.lesson_count:
            return "—"

        return str(obj.lesson_count)

    class Media:
        css = {
            "all": ("admin/condensed_lessons.css",),
        }
