from datetime import datetime, timezone

import pytest

from apps.lms.models import Lesson

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase", "purchase_of_another_course"),
]


@pytest.fixture(autouse=True)
def group(mixer, course, another_course):
    """Let all courses in the suite be in the same group"""
    group = mixer.blend("products.Group")

    course.update(group=group)
    another_course.update(group=group)

    return group


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

    assert "*" in got["markdown_text"], "The field is not rendered"
    assert "<em>" not in got["markdown_text"], "The field is not rendered"
    assert "<em>should be rendered" in got["course"]["homework_check_recommendations"]


def test_breadcrumbs(api, question, purchase):
    lesson = question.lesson_set.first()

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["breadcrumbs"]["lesson"]["id"] == lesson.pk
    assert got["breadcrumbs"]["module"]["id"] == lesson.module.pk
    assert got["breadcrumbs"]["course"]["id"] == purchase.course.id

    assert got["course"]["id"] == purchase.course.id
    assert got["course"]["slug"] == purchase.course.slug
    assert got["course"]["name"] == purchase.course.name


@pytest.mark.usefixtures("group", "_set_current_user")
def test_breadcrums_if_user_purchased_same_course_from_the_group(api, question, question_of_another_course, purchase, purchase_of_another_course):
    purchase_of_another_course.refund()
    lesson = question.lesson_set.first()

    got = api.get(f"/api/v2/homework/questions/{question_of_another_course.slug}/")

    assert got["breadcrumbs"]["lesson"]["id"] == lesson.pk
    assert got["breadcrumbs"]["module"]["id"] == lesson.module.pk
    assert got["breadcrumbs"]["course"]["id"] == purchase.course.id

    assert got["course"]["id"] == purchase.course.id
    assert got["course"]["slug"] == purchase.course.slug
    assert got["course"]["name"] == purchase.course.name


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
    assert not api.user.has_perm("studying.purchased_all_courses")

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=404)


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, question):
    api.user.update(is_superuser=True)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


@pytest.mark.usefixtures("group", "_set_current_user")
def test_fail_if_user_has_not_purchased_same_course_from_the_group(api, mixer, purchase, purchase_of_another_course, question):
    """Same as above, just to make sure above test works"""
    purchase.refund()
    purchase_of_another_course.course.update(group=mixer.blend("products.Group"))  # Another group that user has not purchased

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=404)


@pytest.mark.usefixtures("_no_purchase")
@pytest.mark.parametrize(
    "permission",
    [
        "homework.see_all_questions",
        "studying.purchased_all_courses",
    ],
)
def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, question, permission):
    api.user.add_perm(permission)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


def test_no_anon(anon, question):
    anon.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=401)
