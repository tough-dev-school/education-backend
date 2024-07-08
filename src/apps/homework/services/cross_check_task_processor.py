from dataclasses import dataclass

from django.db.models import QuerySet
from django.utils.functional import cached_property

from apps.homework.models import Answer, AnswerCrossCheck
from apps.homework.models.answer_cross_check import CrossCheckTask
from core.services import BaseService


@dataclass
class CrossCheckTaskProcessor(BaseService):
    answer: "Answer"

    def act(self) -> None:
        if self.should_create():
            self.create()

        if self.should_delete():
            self.delete()

    def create(self) -> CrossCheckTask:
        return CrossCheckTask.objects.create(
            answer=self.answer,
            source_cross_check=self.source_cross_check,  # type: ignore
            required_cross_check=self.required_cross_check,
        )

    def delete(self) -> None:
        self.tasks_for_delete_queryset.delete()

    def should_create(self) -> bool:
        return self.required_cross_check is not None and self.source_cross_check is not None

    def should_delete(self) -> bool:
        return self.tasks_for_delete_queryset.exists()

    @cached_property
    def tasks_for_delete_queryset(self) -> "QuerySet[CrossCheckTask]":
        return CrossCheckTask.objects.filter(required_cross_check=self.source_cross_check)

    @cached_property
    def source_cross_check(self) -> "AnswerCrossCheck | None":
        return AnswerCrossCheck.objects.filter(answer=self.answer.parent, checker=self.answer.author).first()

    @cached_property
    def required_cross_check(self) -> "AnswerCrossCheck | None":
        task = CrossCheckTask.objects.filter(source_cross_check__answer=self.answer.parent, source_cross_check__checker=self.answer.author).first()

        if task is not None:
            return task.required_cross_check

        queryset = AnswerCrossCheck.objects.filter(answer__author=self.answer.author, answer__question=self.answer.question).exclude(source_tasks__isnull=False)

        for cross_check in queryset.iterator():
            if not cross_check.is_checked():
                return cross_check
