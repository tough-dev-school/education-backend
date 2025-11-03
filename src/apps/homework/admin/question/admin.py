from typing import no_type_check

from django.db.models import OuterRef, QuerySet, Subquery
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from apps.homework import tasks
from apps.homework.admin.question.form import QuestionForm
from apps.homework.models import Question
from apps.products.models import Course
from core.admin import ModelAdmin, admin
from core.admin.actions import archive
from core.admin.filters import ArchivedFilter


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = [
        "name",
        "product",
        "tariff",
    ]
    list_filter = [
        ArchivedFilter,
        "lesson__module__course__group",
    ]
    fields = [
        "module",
        "lesson",
        "name",
        "internal_name",
        "deadline",
        "text",
    ]
    actions = [
        "dispatch_crosscheck",
        archive.archive,
        archive.unarchive,
    ]
    save_as = True
    form = QuestionForm

    @admin.display(description=_("Course"))
    def product(self, question: Question) -> str:
        return getattr(question, "product_name", "-") or "-"

    @admin.display(description=_("Tariff Name"))
    def tariff(self, question: Question) -> str:
        return getattr(question, "course_name", "-") or "-"

    @no_type_check
    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        queryset = super().get_queryset(request)

        tariff = Course.objects.filter(
            modules__lesson__question=OuterRef("pk"),
        ).values("tariff_name")[:1]

        group = Course.objects.filter(
            modules__lesson__question=OuterRef("pk"),
        ).values("group__name")[:1]

        return queryset.annotate(
            course_name=Subquery(tariff),
            product_name=Subquery(group),
        )

    @admin.action(description=_("Dispatch crosscheck"))
    def dispatch_crosscheck(self, request: Request, queryset: QuerySet) -> None:
        for question in queryset.iterator():
            tasks.dispatch_crosscheck.delay(question_id=question.id)

        self.message_user(request, f"Crosscheck dispatched for {queryset.count()} questions")
