from app.celery import celery
from homework.models import Question


@celery.task
def disptach_crosscheck(question_id, *args, **kwargs):
    question = Question.objects.get(pk=question_id)
    question.dispatch_crosscheck(*args, **kwargs)
