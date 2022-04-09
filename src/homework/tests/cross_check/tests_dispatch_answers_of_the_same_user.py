import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(10),  # we have to repeat this test suite because the method does randomizing
]


@pytest.fixture
def answers(mixer, question, user):
    return mixer.cycle(2).blend('homework.Answer', question=question, author=user, parent=None)


@pytest.fixture
def service(dispatcher, answers):
    return dispatcher(answers=answers)


@pytest.fixture
def get_answer_to_check(service):
    def _get_answer_to_check(user):
        return service.get_answer_to_check(user)

    return _get_answer_to_check


@pytest.fixture
def give_answer_to_user(service):
    def _give_answer_to_user(answer, user):
        return service.give_answer_to_user(answer, user)

    return _give_answer_to_user


def test_first_answer_is_got(get_answer_to_check, answers, another_user):
    assert get_answer_to_check(another_user) == answers[0]


def test_other_answers_are_ignored(get_answer_to_check, give_answer_to_user, another_user):
    _ = give_answer_to_user(get_answer_to_check(another_user), another_user)
    assert get_answer_to_check(another_user) is None
