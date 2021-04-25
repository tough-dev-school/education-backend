import pytest

from homework.services import AnswerCrossCheckDispatcher, QuestionAnswerCrossCheckDispatcher

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def dispatcher():
    return AnswerCrossCheckDispatcher


@pytest.fixture
def question_dispatcher(question):
    return QuestionAnswerCrossCheckDispatcher(question=question, answers_per_user=1)


@pytest.fixture
def question(mixer):
    return mixer.blend('homework.Question')


@pytest.fixture(autouse=True)
def answers(mixer, question, user, another_user):
    return [
        mixer.blend('homework.Answer', question=question, author=user),
        mixer.blend('homework.Answer', question=question, author=another_user),
    ]
