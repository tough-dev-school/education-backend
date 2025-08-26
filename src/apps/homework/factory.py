from apps.homework.models import Question
from apps.products.models import Course
from core.test.factory import FixtureFactory, register


@register
def question(self: FixtureFactory, course: Course | None = None, name: str | None = None, **kwargs: dict) -> Question:
    question = Question.objects.create(
        name=name or f"Please {self.faker.bs()} two times",
        **kwargs,
    )

    if course is not None:
        module = self.module(course=course)
        self.lesson(module=module, question=question)

    return question
