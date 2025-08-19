import pytest

from apps.homework.services import NewAnswerNotifier


@pytest.fixture
def notifier():
    return NewAnswerNotifier


@pytest.fixture
def question(factory, course):
    return factory.question(course=course, name="Вторая домашка")


@pytest.fixture
def another_answer(mixer, question):
    return mixer.blend("homework.Answer", question=question)


@pytest.fixture
def parent_of_another_answer(mixer, another_answer, question):
    answer = mixer.blend("homework.Answer", question=question)

    another_answer.update(parent=answer)

    return answer
