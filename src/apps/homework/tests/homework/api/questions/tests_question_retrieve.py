from datetime import datetime, timezone

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


def test_ok(api, question):
    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["slug"] == str(question.slug)
    assert got["name"] == question.name


@pytest.mark.usefixtures("kamchatka_timezone")
def test_question_deadline(api, question):
    question.update(deadline=datetime(2032, 12, 24, 15, 13, tzinfo=timezone.utc))

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["deadline"] == "2032-12-25T03:13:00+12:00"


def test_markdown(api, question):
    question.update(text="*should be rendered*")

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert "<em>should be rendered" in got["text"]


def test_empty_breadcrumbs(api, question):
    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["breadcrumbs"] is None


def test_breadcrumbs(api, question, factory):
    module = factory.module(course=question.courses.first())
    lesson = factory.lesson(module=module, question=question)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["breadcrumbs"]["lesson"]["id"] == lesson.pk
    assert got["breadcrumbs"]["module"]["id"] == module.pk
    assert got["breadcrumbs"]["course"]["id"] == module.course_id


@pytest.mark.usefixtures("_no_purchase")
def test_403_for_not_purchased_users(api, question):
    assert api.user.is_superuser is False
    assert not api.user.has_perm("homework.see_all_questions")

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=403)


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, question):
    api.user.update(is_superuser=True)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, question):
    api.user.add_perm("homework.question.see_all_questions")

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


@pytest.mark.usefixtures("_no_purchase")
def test_ok_if_user_has_not_purchased_but_permission_check_is_disabled(api, settings, question):
    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = True

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


def test_no_anon(anon, question):
    anon.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=404)
