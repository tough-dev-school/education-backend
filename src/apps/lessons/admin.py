from adminsortable2.admin import SortableAdminBase, SortableTabularInline

from apps.lessons.models import Course, Lesson
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


@admin.register(Course)
class CourseAdmin(SortableAdminBase, ModelAdmin):
    fields = [
        "name",
    ]
    readonly_fields = [
        "name",
    ]

    inlines = [LessonInline]
