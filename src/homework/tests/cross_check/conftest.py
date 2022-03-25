import pytest

from homework.services import AnswerCrossCheckDispatcher, QuestionCrossCheckDispatcher

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def dispatcher():
    return AnswerCrossCheckDispatcher


@pytest.fixture
def question_dispatcher(question):
    return QuestionCrossCheckDispatcher(question=question, answers_per_user=1)


@pytest.fixture
def question(mixer):
    return mixer.blend('homework.Question')


@pytest.fixture(autouse=True)
def answers(mixer, question, user, another_user):
    return [
        mixer.blend('homework.Answer', question=question, author=user, parent=None),
        mixer.blend('homework.Answer', question=question, author=another_user, parent=None),
    ]


@pytest.fixture(autouse=True)
def answers_of_the_same_user(mixer, question, user, another_user):
    return [
        mixer.blend('homework.Answer', question=question, author=user, parent=None),
        mixer.blend('homework.Answer', question=question, author=user, parent=None),
    ]
