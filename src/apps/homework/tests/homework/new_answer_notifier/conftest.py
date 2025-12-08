import pytest

from apps.homework.services import NewAnswerNotifier


@pytest.fixture
def notifier():
    return NewAnswerNotifier


@pytest.fixture
def question(factory, course):
    return factory.question(course=course, name="Вторая домашка")


@pytest.fixture
def another_answer(factory, question):
    return factory.answer(question=question)


@pytest.fixture
def parent_of_another_answer(factory, another_answer, question):
    answer = factory.answer(question=question)

    another_answer.update(parent=answer)

    return answer
