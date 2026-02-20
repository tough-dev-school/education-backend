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
def crosscheck(mixer, question, user, another_user):
    answer = mixer.blend("homework.Answer", question=question, author=another_user)
    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=user)


@pytest.fixture
def crosscheck_for_question_of_another_course(mixer, question_of_another_course, user):
    answer = mixer.blend("homework.Answer", question=question_of_another_course)

    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=user)


@pytest.fixture
def another_crosscheck(mixer, question, user, another_user):
    answer = mixer.blend("homework.Answer", question=question, author=another_user)
    return mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=user, checked=datetime(2032, 1, 1, tzinfo=timezone.utc))


def test_question_is_required(api):
    got = api.get("/api/v2/homework/crosschecks/", expected_status_code=400)

    assert "question" in got[0]


def test_nonexistant_question(api):
    api.get("/api/v2/homework/crosschecks/?question=nonexistan", expected_status_code=400)


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


@pytest.mark.xfail(reason="We do not check if user has purchased a course, cuz such users get no crosschecks dispatched", strict=True)
@pytest.mark.usefixtures("crosscheck", "_no_purchase")
def test_no_crosschecks_for_not_purchased_courses(api, question):
    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 0


@pytest.mark.parametrize(("checked", "is_checked"), [(None, False), (datetime(2032, 1, 1, tzinfo=timezone.utc), True)])
def test_is_checked(api, question, crosscheck, checked, is_checked):
    crosscheck.update(checked=checked)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")[0]

    assert got["is_checked"] is is_checked


def test_excludes_cross_check_from_another_checker(api, question, crosscheck, another_user):
    crosscheck.update(checker=another_user)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 0


def test_excludes_cross_check_where_user_is_answer_author(api, question, mixer):
    """Crosschecks where the user checks their own answer should be excluded"""
    own_answer = mixer.blend("homework.Answer", question=question, author=api.user)
    mixer.blend("homework.AnswerCrossCheck", answer=own_answer, checker=api.user)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 0


def test_excludes_cross_check_created_by_user(api, question, mixer, another_user):
    """Crosschecks created by the user (author=user) should be excluded"""
    answer = mixer.blend("homework.Answer", question=question, author=another_user)
    mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=api.user, author=api.user)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 0


@pytest.mark.usefixtures("crosscheck")
def test_excludes_cross_check_from_another_question(api, mixer, another_question, question, another_answer):
    """Generate a crosscheck for another question for the same course and make sure GET param filter ignores it"""

    another_answer = mixer.blend("homework.Answer", question=another_question)
    mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=api.user)

    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 1, "Should be only crosscheck for question"


@pytest.mark.usefixtures("crosscheck", "crosscheck_for_question_of_another_course")
def test_includes_crosschecks_for_questions_from_another_course_if_courses_match_the_group(api, question, question_of_another_course):
    assert question_of_another_course.lesson_set.first().module.course.group == question.lesson_set.first().module.course.group
    got = api.get(f"/api/v2/homework/crosschecks/?question={question.slug}")

    assert len(got) == 2, "crosscheck_for_question_of_another_course should be included"


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
