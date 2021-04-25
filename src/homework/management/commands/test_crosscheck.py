from django.core.management.base import BaseCommand

from homework.models import AnswerCrossCheck, Question
from homework.services import AnswerCrossCheckDispatcher


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        question = Question.objects.last()

        AnswerCrossCheck.objects.all().delete()

        for i in range(0, 3):
            dispatcher = AnswerCrossCheckDispatcher(answers=question.answer_set.all())
            print('Iter', i)
            dispatcher()
