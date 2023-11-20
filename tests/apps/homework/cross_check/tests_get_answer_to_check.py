import pytest

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(10),  # we have to repeat this test suite because the method does randomizing
]


@pytest.fixture
def get(dispatcher, answers):
    def _get(user):
        service = dispatcher(answers=answers)

        return service.get_answer_to_check(user)

    return _get


def test_already_checked_answers_are_excluded(get, user, mixer, answers):
    mixer.blend("homework.AnswerCrossCheck", answer=answers[0], checker=user)

    assert get(user) != answers[0]


def test_answers_with_exclude_flag_are_excluded(get, user):
    Answer.objects.all().update(do_not_crosscheck=True)

    assert get(user) is None


def test_answer_authors_are_excluded(get, user, answers):
    answers[0].update(author=user)

    assert get(user) != answers[0]


def test_answers_without_crosschecks_are_preferred(get, user, another_user, mixer, answers):
    mixer.blend("homework.AnswerCrossCheck", answer=answers[1], checker=user)

    assert get(another_user) == answers[0]
