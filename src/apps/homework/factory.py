from apps.homework.models import Question
from apps.products.models import Course
from core.test.factory import FixtureFactory, register


@register
def question(self: FixtureFactory, course: Course | None = None, **kwargs: dict) -> Question:
    question = self.mixer.blend("homework.Question", _legacy_course=None, **kwargs)

    if course is not None:
        module = self.module(course=course)
        self.lesson(module=module, question=question)

    return question
