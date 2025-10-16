import pytest
from django.utils import timezone

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


@pytest.fixture(autouse=True)
def answers(mixer, question, api, another_user):
    return [
        mixer.blend("homework.Answer", question=question, author=api.user, parent=None),
        mixer.blend("homework.Answer", question=question, author=another_user, parent=None),
    ]


@pytest.fixture(autouse=True)
def crosscheck(mixer, answers, api):
    return mixer.blend("homework.AnswerCrossCheck", answer=answers[1], checker=api.user)


@pytest.fixture
def crosscheck_for_question_of_another_course(mixer, question_of_another_course, api):
    answer = mixer.blend("homework.Answer", question=question_of_another_course)

    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=api.user)


def test_no_crosscheckes(api, question, crosscheck):
    crosscheck.delete()

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 0
    assert got["homework"]["crosschecks"]["checked"] == 0


def test_not_checked(api, question):
    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 1
    assert got["homework"]["crosschecks"]["checked"] == 0


def test_checked(api, question, crosscheck):
    crosscheck.update(checked=timezone.now())

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 1
    assert got["homework"]["crosschecks"]["checked"] == 1


def test_three_crosschecks(api, question, mixer):
    """Generate two additional crosschecks"""
    mixer.cycle(2).blend("homework.AnswerCrossCheck", answer__question=question, checker=api.user)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 3


@pytest.mark.usefixtures("crosscheck_for_question_of_another_course")
def test_crosscheck_for_the_question_of_another_course(api, question):
    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 2
    assert got["homework"]["crosschecks"]["checked"] == 0


def test_non_user_crosschecks_are_ignored(api, question, crosscheck, another_user):
    crosscheck.update(checker=another_user)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 0


def test_non_lesson_crosschecks_are_ignored(api, question, crosscheck, another_question):
    crosscheck.answer.update(question=another_question)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 0


def test_crosscheckes_where_current_user_is_author_are_ignored(api, question, crosscheck, answers, another_user):
    """Check if crosschecks where someone else checks user's answer are ignored"""
    crosscheck.update(answer=answers[0], checker=another_user)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["homework"]["crosschecks"]["total"] == 0
