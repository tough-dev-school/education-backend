import pytest
from django.utils import timezone

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def answers(mixer, question, api, another_user):
    return [
        mixer.blend("homework.Answer", question=question, author=api.user, parent=None),
        mixer.blend("homework.Answer", question=question, author=another_user, parent=None),
    ]


@pytest.fixture(autouse=True)
def crosscheck(mixer, answers, api):
    return mixer.blend("homework.AnswerCrossCheck", answer=answers[1], checker=api.user)


def test_no_crosscheckes(api, module, lesson, crosscheck):
    crosscheck.delete()

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["homework"]["crosschecks"]["total"] == 0
    assert got["results"][0]["homework"]["crosschecks"]["checked"] == 0


def test_not_checked(api, module):
    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["crosschecks"]["total"] == 1
    assert got["results"][0]["homework"]["crosschecks"]["checked"] == 0


def test_checked(api, module, crosscheck):
    crosscheck.update(checked=timezone.now())

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["crosschecks"]["total"] == 1
    assert got["results"][0]["homework"]["crosschecks"]["checked"] == 1


def test_three_crosschecks(api, module, question, mixer):
    """Generate two additional crosschecks"""
    mixer.cycle(2).blend("homework.AnswerCrossCheck", answer__question=question, checker=api.user)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["crosschecks"]["total"] == 3


def test_non_user_crosschecks_are_ignored(api, module, crosscheck, another_user):
    crosscheck.update(checker=another_user)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["crosschecks"]["total"] == 0


def test_non_lesson_crosschecks_are_ignored(api, module, crosscheck, another_question):
    crosscheck.answer.update(question=another_question)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["crosschecks"]["total"] == 0


def test_crosscheckes_where_current_user_is_author_are_ignored(api, module, crosscheck, answers, another_user):
    """Check if crosschecks where someone else checks user's answer are ignored"""
    crosscheck.update(answer=answers[0], checker=another_user)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["crosschecks"]["total"] == 0
