from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from apps.homework.admin.answer.filters import IsRootFilter
from apps.homework.models import Answer, AnswerCrossCheck
from core.admin import ModelAdmin, admin


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_filter = [
        IsRootFilter,
        "question",
        "question__courses",
    ]
    list_display = [
        "created",
        "question",
        "course",
        "_author",
        "do_not_crosscheck",
        "crosscheck_count",
    ]
    fields = [
        "created",
        "author",
        "parent",
        "text",
    ]
    readonly_fields = [
        "created",
        "author",
        "text",
    ]
    raw_id_fields = [
        "parent",
    ]

    list_editable = [
        "do_not_crosscheck",
    ]

    search_fields = [
        "author__first_name",
        "author__last_name",
        "author__email",
        "text",
    ]

    def get_queryset(self, request: Request) -> QuerySet:  # type: ignore
        return super().get_queryset(request).with_crosscheck_count().select_related("author", "question")  # type: ignore

    @admin.display(description=_("Course"))
    def course(self, obj: Answer) -> str:
        course = obj.get_purchased_course()
        if course is None:
            return "—"

        return str(course)

    @admin.display(description=_("Crosschecking people"), ordering="crosscheck_count")
    def crosscheck_count(self, obj: Answer) -> str:
        return obj.crosscheck_count or "—"

    @mark_safe
    @admin.display(description=_("Author"), ordering="author")
    def _author(self, obj: Answer) -> str:
        author_url = reverse("admin:users_student_change", args=[obj.author_id])
        return f'<a href="{author_url}">{obj.author}</a>'


@admin.register(AnswerCrossCheck)
class AnswerCrossCheckAdmin(ModelAdmin):
    fields = (
        "course",
        "question",
        "checked_at",
        "author",
        "view",
    )
    list_display = fields
    readonly_fields = (
        "question",
        "course",
        "checked_at",
        "author",
        "view",
    )
    list_filter = (
        "answer__question",
        "answer__question__courses",
    )

    def get_queryset(self, request: Request) -> QuerySet:  # type: ignore
        return super().get_queryset(request).select_related("answer", "answer__question", "answer__author")

    @admin.display(description=_("Course"))
    def course(self, obj: AnswerCrossCheck) -> str:
        course = obj.answer.get_purchased_course()
        if course is None:
            return "—"

        return str(course)

    @admin.display(description=_("Question"), ordering="answer__question")
    def question(self, obj: AnswerCrossCheck) -> str:
        return str(obj.answer.question)

    @admin.display(description=_("Author"), ordering="answer__author")
    def author(self, obj: AnswerCrossCheck) -> str:
        return str(obj.answer.author)

    @admin.display(description=_("View"))
    @mark_safe
    def view(self, obj: AnswerCrossCheck) -> str:
        return f"<a href={obj.answer.get_absolute_url()}>Смотреть на сайте</a>"
