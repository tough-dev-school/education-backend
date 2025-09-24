from datetime import datetime, timezone

import pytest

from apps.homework.models import AnswerCrossCheck

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def user(api):
    return api.user


@pytest.fixture
def crosscheck(mixer, answer, user):
    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=user)


@pytest.fixture
def another_crosscheck(mixer, another_answer, user):
    return mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=user, checked=datetime(2032, 1, 1, tzinfo=timezone.utc))


def test_question_is_required(api):
    got = api.get("/api/v2/homework/crosschecks/", expected_status_code=400)

    assert "question" in got


def test_as_anonymous(anon):
    anon.get("/api/v2/homework/crosschecks/?question=slug", expected_status_code=401)


def test_base_response(api, question, crosscheck):
    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")[0]

    assert got["id"] == crosscheck.id

    assert got["answer"]["url"] == crosscheck.answer.get_absolute_url()
    assert got["answer"]["slug"] == str(crosscheck.answer.slug)

    assert got["answer"]["author"]["uuid"] == str(crosscheck.answer.author.uuid)
    assert got["answer"]["author"]["first_name"] == crosscheck.answer.author.first_name
    assert got["answer"]["author"]["last_name"] == crosscheck.answer.author.last_name
    assert got["answer"]["author"]["avatar"] is None

    assert got["answer"]["question"]["slug"] == str(question.slug)
    assert got["answer"]["question"]["name"] == question.name
    assert "markdown_text" in got["answer"]["question"]


@pytest.mark.parametrize(("checked", "is_checked"), [(None, False), (datetime(2032, 1, 1, tzinfo=timezone.utc), True)])
def test_is_checked(api, question, crosscheck, checked, is_checked):
    crosscheck.update(checked=checked)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")[0]

    assert got["is_checked"] is is_checked


def test_exclude_cross_check_from_another_checker(api, question, crosscheck, another_user):
    crosscheck.update(checker=another_user)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 0


@pytest.mark.usefixtures("crosscheck")
def test_exclude_cross_check_from_another_question(api, another_question):
    got = api.get(f"/api/v2/homework/crosschecks/?question={another_question.slug}")

    assert len(got) == 0


def test_crosschecks_are_ordered_by_pk_1(api, question, crosscheck, another_crosscheck):
    AnswerCrossCheck.objects.filter(id=crosscheck.id).update(id=100_500)
    AnswerCrossCheck.objects.filter(id=another_crosscheck.id).update(id=100)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert got[0]["id"] == 100
    assert got[1]["id"] == 100_500


def test_crosschecks_are_ordered_by_pk_2(api, question, crosscheck, another_crosscheck):
    AnswerCrossCheck.objects.filter(id=crosscheck.id).update(id=100)
    AnswerCrossCheck.objects.filter(id=another_crosscheck.id).update(id=100_500)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert got[0]["id"] == 100
    assert got[1]["id"] == 100_500
