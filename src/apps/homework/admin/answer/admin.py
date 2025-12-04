from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.homework.admin.answer.filters import IsRootFilter
from apps.homework.models import Answer
from core.admin import ModelAdmin, admin


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_filter = [
        IsRootFilter,
        "question",
        "study__course",
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
        "legacy_text",
    ]
    readonly_fields = [
        "created",
        "author",
        "legacy_text",
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
        "legacy_text",
        "content",
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).with_crosscheck_count().select_related("author", "question", "study__course__group")  # type: ignore

    @admin.display(description=_("Course"))
    def course(self, obj: Answer) -> str:
        if obj.study is not None:
            return str(obj.study.course)

        else:
            return "—"

    @admin.display(description=_("Crosschecking people"), ordering="crosscheck_count")
    def crosscheck_count(self, obj: Answer) -> str:
        return obj.crosscheck_count or "—"

    @mark_safe
    @admin.display(description=_("Author"), ordering="author")
    def _author(self, obj: Answer) -> str:
        author_url = reverse("admin:users_adminuserproxy_change", args=[obj.author_id])
        return f'<a href="{author_url}">{obj.author}</a>'
