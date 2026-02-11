from apps.homework.models import Answer, Question
from apps.homework.services import NewAnswerNotifier
from apps.users.models import User
from core.celery import celery


class AnswerDeletedBeforeNotification(Answer.DoesNotExist):
    """Explifit exception for cleaner sentry logs"""


@celery.task
def dispatch_crosscheck(question_id: str, author_id: int) -> None:
    question = Question.objects.get(pk=question_id)
    author = User.objects.get(pk=author_id)
    question.dispatch_crosscheck(author=author)


@celery.task
def notify_about_new_answer(answer_id: str) -> None:
    try:
        answer = Answer.objects.get(pk=answer_id)
    except Answer.DoesNotExist:
        raise AnswerDeletedBeforeNotification

    notifier = NewAnswerNotifier(answer)

    notifier()
