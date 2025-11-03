from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.homework.models import AnswerCrossCheck
from core.admin import ModelAdmin, admin


@admin.register(AnswerCrossCheck)
class AnswerCrossCheckAdmin(ModelAdmin):
    fields = (
        "course",
        "question",
        "checked",
        "author",
        "view",
    )
    list_display = fields
    readonly_fields = (
        "question",
        "course",
        "checked",
        "author",
        "view",
    )
    list_filter = ("answer__question",)
    list_select_related = (
        "answer",
        "answer__question",
        "answer__author",
        "answer__study__course",
        "answer__study__course__group",
    )
    actions = [
        "delete_selected",
    ]

    @admin.display(description=_("Course"))
    def course(self, obj: AnswerCrossCheck) -> str:
        if obj.answer.study is not None:
            return str(obj.answer.study.course)

        return "—"

    @admin.display(description=_("Question"), ordering="answer__question")
    def question(self, obj: AnswerCrossCheck) -> str:
        return obj.answer.question.name

    @admin.display(description=_("Author"), ordering="answer__author")
    def author(self, obj: AnswerCrossCheck) -> str:
        return str(obj.answer.author)

    @admin.display(description=_("View"))
    @mark_safe
    def view(self, obj: AnswerCrossCheck) -> str:
        return f"<a href={obj.answer.get_absolute_url()}>Смотреть на сайте</a>"
