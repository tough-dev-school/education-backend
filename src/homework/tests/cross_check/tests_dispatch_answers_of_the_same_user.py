import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(10),  # we have to repeat this test suite because the method does randomizing
]


@pytest.fixture
def answers(mixer, question, user):
    return [
        mixer.blend('homework.Answer', question=question, author=user, parent=None),
        mixer.blend('homework.Answer', question=question, author=user, parent=None),
    ]


@pytest.fixture
def service(dispatcher, answers):
    return dispatcher(answers=answers)


@pytest.fixture
def get(service):
    def _get(user):
        return service.get_answer_to_check(user)

    return _get


@pytest.fixture
def give(service):
    def _give(user, answer):
        return service.give_answer_to_user(answer, user)

    return _give


def test_first_answer_is_got(get, answers, another_user):
    assert get(another_user) == answers[0]


def test_other_answers_are_ignored(get, give, another_user):
    _ = give(another_user, get(another_user))
    assert get(another_user) is None
