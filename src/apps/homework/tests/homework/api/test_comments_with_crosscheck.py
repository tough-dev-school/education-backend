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


@pytest.fixture
def get_comments(api) -> "Callable":
    return lambda slug: api.get(f"/api/v2/homework/comments/?answer={slug}")[0]["descendants"]


@pytest.fixture
def _another_checks(mixer, answers, check_crosscheck):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=answers[0])
    ya_crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=answers[0])
    check_crosscheck(crosscheck)
    check_crosscheck(ya_crosscheck)


@pytest.mark.usefixtures("crosschecks")
@pytest.mark.usefixtures("_another_checks")
def test_can_see_only_non_crosschecked_answers(get_comments, answers):
    got = get_comments(answers[0].slug)

    assert len(got) == 5


@pytest.mark.usefixtures("_another_checks")
def test_can_see_only_one_crosschecked_answer(get_comments, answers, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[0])  # my check
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = get_comments(answers[0].slug)

    assert len(got) == 6


@pytest.mark.usefixtures("_another_checks")
def test_can_see_all_answers(get_comments, answers, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[0])  # my check
    check_crosscheck(crosschecks[1])  # my check
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = get_comments(answers[0].slug)

    assert len(got) == 8


def test_ordering(get_comments, answers, crosschecks, check_crosscheck):
    check_crosscheck(crosschecks[0])  # my check
    check_crosscheck(crosschecks[1])  # my check
    check_crosscheck(crosschecks[2])
    check_crosscheck(crosschecks[3])

    got = get_comments(answers[0].slug)

    assert got[0]["created"] < got[1]["created"]
    assert got[1]["created"] < got[2]["created"]
    assert got[2]["created"] < got[3]["created"]
    assert got[3]["created"] < got[4]["created"]
    assert got[4]["created"] < got[5]["created"]
