from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from apps.diplomas.models import Diploma
from apps.diplomas.models import DiplomaStudyProxy
from apps.diplomas.models import Languages
from apps.studying.models import Study
from core.admin import admin
from core.admin import ModelAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest


class DiplomaInline(admin.TabularInline):
    extra = 0
    fields = ("language", "image")
    max_num = 2
    model = Diploma


@admin.register(DiplomaStudyProxy)
class StudyAdmin(ModelAdmin):
    fields = ("course", "student", "homework_accepted")
    inlines = (DiplomaInline,)
    list_display = ("course", "student", "email", "username", "homework_accepted", "en_diploma_exists", "ru_diploma_exists")
    list_filter = ("course", "homework_accepted")
    readonly_fields = ("course", "student")
    search_fields = ("course__name", "student__email", "student__first_name", "student__last_name", "student__username")

    def has_add_permission(self, request: "HttpRequest") -> bool:
        """Study addition is disabled: the student is automatically enrolled in the course when the course is purchased.

        The course can be purchased through the “Order” interface."""
        return False

    @admin.display(description=_("Email"))
    def email(self, study: "Study") -> str:
        return study.student.email

    @admin.display(boolean=True, description=_("EN diploma exists"))
    def en_diploma_exists(self, study: "Study") -> bool:
        return study.diplomas.filter(language=Languages.EN).exists()

    @admin.display(boolean=True, description=_("RU diploma exists"))
    def ru_diploma_exists(self, study: "Study") -> bool:
        return study.diplomas.filter(language=Languages.RU).exists()

    @admin.display(description=_("Username"))
    def username(self, study: "Study") -> str:
        return study.student.username
