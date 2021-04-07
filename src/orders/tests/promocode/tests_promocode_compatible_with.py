import pytest

pytestmark = [pytest.mark.django_db]


def test_true_if_no_courses_are_attached(promocode, course):
    assert promocode.compatible_with(course) is True


def test_false_if_some_courses_are_attached_but_given_is_not_attached(promocode, course, another_course):
    promocode.courses.add(course)

    assert promocode.compatible_with(another_course) is False


def test_true_if_course_is_attached(promocode, course):
    promocode.courses.add(course)

    assert promocode.compatible_with(course) is True
