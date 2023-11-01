from typing import TYPE_CHECKING

from admin_auto_filters.filters import AutocompleteFilter  # type: ignore[import-untyped]

from apps.diplomas.models import Diploma
from apps.studying.models import Study
from core.admin import admin
from core.admin import ModelAdmin

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class CourseFilter(AutocompleteFilter):
    title = "Курс"
    field_name = "course"


class StudentFilter(AutocompleteFilter):
    title = "студент"
    field_name = "student"

    def get_autocomplete_url(self, request: "HttpRequest", model_admin: "ModelAdmin") -> str:
        del model_admin

        course = request.GET.get("course__pk__exact")

        return f"/admin/autocomplete/?course={course}"


class DiplomaInline(admin.TabularInline):
    extra = 1
    fields = ("slug", "language", "image")
    model = Diploma
    readonly_fields = ("slug",)


@admin.register(Study)
class StudyAdmin(ModelAdmin):
    actions = ("graduate",)
    autocomplete_fields = ("course", "student")
    fields = ("course", "student", "homework_accepted")
    inlines = (DiplomaInline,)
    list_display = ("course", "student", "homework_accepted")
    list_filter = (CourseFilter, StudentFilter, "homework_accepted")
    readonly_fields = ("course", "student", "homework_accepted")

    def has_add_permission(self, request: "HttpRequest") -> bool:
        """Study addition is disabled: the student is automatically enrolled in the course when the course is purchased.

        The course can be purchased through the “Order” interface."""
        del request

        return False

    @admin.action(description="Создать дипломы на желаемых студентами языках и разослать их по почте")
    def graduate(self, request: "HttpRequest", queryset: "QuerySet") -> None:
        pass
