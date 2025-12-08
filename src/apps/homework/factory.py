from apps.homework.models import Answer, Question
from apps.products.models import Course
from apps.users.models import User
from core.test.factory import FixtureFactory, register


@register
def question(
    self: FixtureFactory,
    course: Course | None = None,
    name: str | None = None,
    **kwargs: dict,
) -> Question:
    question = Question.objects.create(
        name=name or f"Please {self.faker.bs()} two times",
        **kwargs,
    )

    if course is not None:
        module = self.module(course=course)
        self.lesson(module=module, question=question)

    return question


@register
def answer(
    self: FixtureFactory,
    question: Question,
    text: str | None = None,
    author: User | None = None,
    **kwargs: dict,
) -> Answer:
    return Answer.objects.create(
        question=question,
        author=author or self.mixer.blend("users.User"),
        content=self.prosemirror(text if text is not None else self.faker.text()),
        **kwargs,
    )
