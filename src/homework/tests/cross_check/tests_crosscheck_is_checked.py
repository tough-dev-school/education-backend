import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def answer(answers):
    return answers[0]


@pytest.fixture
def crosscheck(mixer, answer, another_user):
    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=another_user)


def test_not_by_default(crosscheck):
    assert crosscheck.is_checked() is False


def test_checked_if_there_are_comments_from_checker(crosscheck, mixer, another_user, answer):
    mixer.blend("homework.Answer", parent=answer, author=another_user)

    assert crosscheck.is_checked() is True


def test_not_checked_if_answers_are_not_children_of_the_checked_answer(crosscheck, mixer, another_user, answer):
    mixer.blend("homework.Answer", author=another_user)

    assert crosscheck.is_checked() is False
