from typing import TYPE_CHECKING

from apps.diplomas.models import Diploma
from apps.studying.models import Study
from core.admin import admin
from core.admin import ModelAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest


class DiplomaInline(admin.TabularInline):
    extra = 0
    fields = ("slug", "language", "image")
    max_num = 2
    model = Diploma
    readonly_fields = ("slug",)


@admin.register(Study)
class StudyAdmin(ModelAdmin):
    fields = ("course", "student", "homework_accepted")
    inlines = (DiplomaInline,)
    list_display = ("course", "student", "homework_accepted")
    list_filter = ("course", "student", "homework_accepted")
    readonly_fields = ("course", "student")
    search_fields = ("course__name", "student__first_name", "student__last_name")

    def has_add_permission(self, request: "HttpRequest") -> bool:
        """Study addition is disabled: the student is automatically enrolled in the course when the course is purchased.

        The course can be purchased through the “Order” interface."""
        return False
