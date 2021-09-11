import uuid
from hattori.base import BaseAnonymizer, faker

from homework.models import Answer, Question


class SlugAnonymizer(BaseAnonymizer):
    def run(self, *args, **kwargs):
        result = super().run(*args, **kwargs)

        self.replace_uuids()

        return result

    def replace_uuids(self):
        """Need this method cuz hattori cant handle uuids"""
        for instance in self.get_query_set().iterator():
            instance.slug = uuid.uuid4()
            instance.save()


class HomeworkAnswerAnonymizer(SlugAnonymizer, BaseAnonymizer):
    model = Answer

    attributes = [
        ('text', faker.paragraph),
    ]


class HomeworkQuestionAnonymizer(SlugAnonymizer, BaseAnonymizer):
    model = Question

    attributes = [
        ('text', faker.paragraph),
    ]
