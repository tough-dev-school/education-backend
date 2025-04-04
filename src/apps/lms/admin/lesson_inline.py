from adminsortable2.admin import SortableTabularInline
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.lms.models import Lesson
from core.admin import admin


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
