import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(10),  # we have to repeat this test suite because the method does randomizing
]


@pytest.fixture
def get(dispatcher, answers, user, another_user):
    def _get(answer):
        service = dispatcher(answers=answers, users=[user, another_user])

        return service.get_user_to_check(answer)

    return _get


def test_already_checking_users_are_excluded(get, user, mixer, answers):
    mixer.blend('homework.AnswerCrossCheck', answer=answers[0], checker=user)

    assert get(answers[0]) != user


def test_answer_authors_are_excluded(get, user, answers):
    answers[0].author = user
    answers[0].save()

    assert get(answers[0]) != user


def test_users_without_crosschecks_are_preferred(get, user, another_user, mixer, answers):
    mixer.blend('homework.AnswerCrossCheck', answer=answers[1], checker=user)

    assert get(answers[0]) == another_user
