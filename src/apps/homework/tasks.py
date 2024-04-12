from typing import Any

from apps.homework.models import Answer, Question
from apps.homework.services import NewAnswerNotifier
from core.celery import celery


@celery.task
def dispatch_crosscheck(question_id: str, *args: Any, **kwargs: dict[str, Any]) -> None:
    question = Question.objects.get(pk=question_id)
    question.dispatch_crosscheck(*args, **kwargs)


@celery.task
def notify_about_new_answer(answer_id: str) -> None:
    answer = Answer.objects.get(pk=answer_id)

    notifier = NewAnswerNotifier(answer)

    notifier()
