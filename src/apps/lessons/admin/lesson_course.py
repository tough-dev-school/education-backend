from adminsortable2.admin import SortableAdminBase, SortableTabularInline
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.lessons.models import Lesson, LessonCourse
from core.admin import ModelAdmin, admin


class LessonInline(SortableTabularInline):
    model = Lesson
    fields = [
        "name",
        "material",
    ]
    raw_id_fields = [
        "material",
    ]


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
