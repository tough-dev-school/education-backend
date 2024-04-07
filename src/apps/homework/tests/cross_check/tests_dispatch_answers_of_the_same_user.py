import pytest

from apps.homework.models import AnswerCrossCheck

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(10),  # we have to repeat this test suite because the method does randomizing
]


@pytest.fixture
def answers(mixer, question, user, another_user):
    return mixer.cycle(2).blend("homework.Answer", question=question, author=user, parent=None) + [
        mixer.blend("homework.Answer", question=question, author=another_user, parent=None)
    ]


@pytest.fixture
def dispatcher(dispatcher, answers):
    return dispatcher(answers=answers)


@pytest.fixture
def get_answer_to_check(dispatcher):
    def _get_answer_to_check(user):
        return dispatcher.get_answer_to_check(user)

    return _get_answer_to_check


def test_first_answer_is_got(get_answer_to_check, answers, another_user):
    assert get_answer_to_check(another_user) == answers[0]


def test_other_answers_are_ignored(dispatcher, answers):
    dispatcher()

    assert AnswerCrossCheck.objects.filter(answer=answers[0]).exists()
    assert not AnswerCrossCheck.objects.filter(answer=answers[1]).exists()
