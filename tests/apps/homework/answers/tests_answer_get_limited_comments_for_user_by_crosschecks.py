from datetime import datetime, timezone
from typing import Callable, List

import pytest

from apps.homework.models import Answer, AnswerCrossCheck
from apps.users.models import User

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def users(mixer, api) -> "List[User]":
    return [
        api.user,
        mixer.blend("users.User"),
        mixer.blend("users.User"),
        mixer.blend("users.User"),
    ]


@pytest.fixture
def question(question):
    question.hide_crosschecked_answers_from_students_without_checks = True
    question.save()
    return question


@pytest.fixture
def answers(mixer, question, users) -> "List[Answer]":
    return [
        mixer.blend("homework.Answer", question=question, author=users[0]),
        mixer.blend("homework.Answer", question=question, author=users[1]),
        mixer.blend("homework.Answer", question=question, author=users[2]),
        mixer.blend("homework.Answer", question=question, author=users[3]),
    ]


@pytest.fixture(autouse=True)
def crosschecks(mixer, answers, users) -> "List[AnswerCrossCheck]":
    return [
        mixer.blend("homework.AnswerCrossCheck", answer=answers[1], checker=users[0], checked_at=None),
        mixer.blend("homework.AnswerCrossCheck", answer=answers[2], checker=users[0], checked_at=None),
        mixer.blend("homework.AnswerCrossCheck", answer=answers[0], checker=users[1], checked_at=None),
        mixer.blend("homework.AnswerCrossCheck", answer=answers[3], checker=users[1], checked_at=None),
    ]


@pytest.fixture
def check_crosscheck(mixer) -> Callable:
    def check(crosscheck: "AnswerCrossCheck") -> Answer:
        crosscheck.checked_at = datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)
        crosscheck.save()
        return mixer.blend("homework.Answer", question=crosscheck.answer.question, parent=crosscheck.answer, author=crosscheck.checker)

    return check


@pytest.fixture(autouse=True)
def answers_on_my_answers(mixer, answers):
    return mixer.cycle(5).blend("homework.Answer", question=answers[0].question, parent=answers[0])


def test_cant_see_answers(answers, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = answers[0].get_limited_comments_for_user_by_crosschecks(answers[0].author)

    assert len(got) == 0


def test_can_all_answers_if_answers_are_not_hidden_by_question_flag(answers, question, crosschecks, check_crosscheck):
    question.hide_crosschecked_answers_from_students_without_checks = False
    question.save()
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = answers[0].get_limited_comments_for_user_by_crosschecks(answers[0].author)

    assert len(got) == 6


def test_another_user_can_see_answers(answers, users, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = answers[0].get_limited_comments_for_user_by_crosschecks(users[1])

    assert len(got) == 6


def test_can_see_only_one_answer(answers, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[0])  # my check
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = answers[0].get_limited_comments_for_user_by_crosschecks(answers[0].author)

    assert len(got) == 1


def test_can_see_all_answers(answers, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[0])  # my check
    check_crosscheck(crosschecks[1])  # my check
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = answers[0].get_limited_comments_for_user_by_crosschecks(answers[0].author)

    assert len(got) == 6
