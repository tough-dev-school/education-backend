from app.celery import celery
from homework.models import Answer, Question
from homework.services import NewAnswerNotifier


@celery.task
def disptach_crosscheck(question_id, *args, **kwargs):
    question = Question.objects.get(pk=question_id)
    question.dispatch_crosscheck(*args, **kwargs)


@celery.task
def notify_about_new_answer(answer_id):
    answer = Answer.objects.get(pk=answer_id)

    notifier = NewAnswerNotifier(answer)

    notifier()
