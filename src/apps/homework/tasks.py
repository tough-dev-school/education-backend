from typing import Any

from apps.homework.models import Answer, Question
from apps.homework.services import NewAnswerNotifier
from core.celery import celery


class AnswerDeletedBeforeNotification(Answer.DoesNotExist):
    """Explifit exception for cleaner sentry logs"""


@celery.task
def dispatch_crosscheck(question_id: str, *args: Any, **kwargs: dict[str, Any]) -> None:
    question = Question.objects.get(pk=question_id)
    question.dispatch_crosscheck(*args, **kwargs)


@celery.task
def notify_about_new_answer(answer_id: str) -> None:
    try:
        answer = Answer.objects.get(pk=answer_id)
    except Answer.DoesNotExist:
        raise AnswerDeletedBeforeNotification

    notifier = NewAnswerNotifier(answer)

    notifier()
