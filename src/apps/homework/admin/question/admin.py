from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from apps.homework import tasks
from apps.homework.admin.question.form import QuestionForm
from apps.homework.models import Question
from core.admin import ModelAdmin, admin


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = [
        "name",
        "course",
    ]
    fields = [
        "module",
        "lesson",
        "name",
        "deadline",
        "text",
    ]
    actions = [
        "dispatch_crosscheck",
    ]
    save_as = True
    form = QuestionForm

    @admin.display(description=_("Course"))
    def course(self, question: Question) -> str:
        lesson = question.lesson_set.select_related("module", "module__course", "module__course__group").first()
        if lesson is None:
            return "-"

        return str(lesson.module.course)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        return super().get_queryset(request).prefetch_related("lesson_set")

    @admin.action(description=_("Dispatch crosscheck"))
    def dispatch_crosscheck(self, request: Request, queryset: QuerySet) -> None:
        for question in queryset.iterator():
            tasks.dispatch_crosscheck.delay(question_id=question.id)

        self.message_user(request, f"Crosscheck dispatched for {queryset.count()} questions")
