import pytest

from homework.services import NewAnswerNotifier


@pytest.fixture
def notifier():
    return NewAnswerNotifier


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def question(mixer, course):
    question = mixer.blend('homework.Question', name='Вторая домашка')
    question.courses.add(course)

    return question


@pytest.fixture
def answer(mixer, question):
    return mixer.blend('homework.Answer', question=question)


@pytest.fixture
def another_answer(mixer):
    return mixer.blend('homework.Answer')


@pytest.fixture
def parent_of_another_answer(mixer, another_answer):
    answer = mixer.blend('homework.Answer')

    another_answer.parent = answer
    another_answer.save()

    return answer
