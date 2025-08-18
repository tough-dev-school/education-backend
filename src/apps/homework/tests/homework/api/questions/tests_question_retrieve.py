from datetime import datetime, timezone

import pytest

from apps.lms.models import Lesson

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase", "purchase_of_another_course"),
]


def test_ok(api, question, course):
    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["slug"] == str(question.slug)
    assert got["name"] == question.name
    assert got["course"]["id"] == course.id
    assert got["course"]["slug"] == course.slug
    assert got["course"]["name"] == course.name


@pytest.mark.usefixtures("kamchatka_timezone")
def test_question_deadline(api, question):
    question.update(deadline=datetime(2032, 12, 24, 15, 13, tzinfo=timezone.utc))

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["deadline"] == "2032-12-25T03:13:00+12:00"


def test_markdown(api, question, course):
    question.update(text="*should be rendered*")
    course.update(homework_check_recommendations="*should be rendered*")

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert "<em>should be rendered" in got["text"]
    assert "<em>should be rendered" in got["course"]["homework_check_recommendations"]


def test_breadcrumbs(api, question, factory, another_course):
    Lesson.objects.filter(question=question).delete()
    module = factory.module(course=another_course)
    lesson = factory.lesson(module=module, question=question)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["breadcrumbs"]["lesson"]["id"] == lesson.pk
    assert got["breadcrumbs"]["module"]["id"] == module.pk
    assert got["breadcrumbs"]["course"]["id"] == another_course.id


def test_course_info_with_attached_lesson(api, question, factory, another_course):
    Lesson.objects.filter(question=question).delete()
    module = factory.module(course=another_course)
    factory.lesson(module=module, question=question)

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["course"]["id"] == another_course.id
    assert got["course"]["name"] == another_course.name


@pytest.mark.usefixtures("_no_purchase")
def test_404_for_not_purchased_users(api, question):
    assert api.user.is_superuser is False
    assert not api.user.has_perm("homework.see_all_questions")

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=404)


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, question):
    api.user.update(is_superuser=True)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, question):
    api.user.add_perm("homework.question.see_all_questions")

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


def test_no_anon(anon, question):
    anon.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=401)
