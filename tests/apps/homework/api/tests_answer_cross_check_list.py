from datetime import datetime, timezone

import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def user(api):
    return api.user


@pytest.fixture
def crosscheck(mixer, answer, user):
    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=user)


def test_question_is_required(api):
    got = api.get("/api/v2/homework/crosschecks/", expected_status_code=400)

    assert "question" in got


def test_as_anonymous(anon):
    anon.get("/api/v2/homework/crosschecks/?question=slug", expected_status_code=401)


def test_base_response(api, question, crosscheck):
    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")[0]

    assert got["answer"]["url"] == crosscheck.answer.get_absolute_url()
    assert got["answer"]["author"]["uuid"] == str(crosscheck.answer.author.uuid)
    assert got["answer"]["author"]["first_name"] == crosscheck.answer.author.first_name
    assert got["answer"]["author"]["last_name"] == crosscheck.answer.author.last_name
    assert got["answer"]["author"]["avatar"] is None


@pytest.mark.parametrize(("checked_at", "is_checked"), [(None, False), (datetime(2032, 1, 1, tzinfo=timezone.utc), True)])
def test_is_checked(api, question, crosscheck, checked_at, is_checked):
    crosscheck.checked_at = checked_at
    crosscheck.save()

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")[0]

    assert got["is_checked"] is is_checked


def test_exclude_cross_check_from_another_checker(api, question, crosscheck, ya_user):
    crosscheck.checker = ya_user
    crosscheck.save()

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 0


@pytest.mark.usefixtures("crosscheck")
def test_exclude_cross_check_from_another_question(api, another_question):
    got = api.get(f"/api/v2/homework/crosschecks/?question={another_question.slug}")

    assert len(got) == 0
