import pytest

pytestmark = [pytest.mark.django_db]


def test_true_if_no_courses_are_attached(ten_percent_promocode, course):
    assert ten_percent_promocode.compatible_with(course) is True


def test_false_if_some_courses_are_attached_but_given_is_not_attached(ten_percent_promocode, course, another_course):
    ten_percent_promocode.courses.add(course)

    assert ten_percent_promocode.compatible_with(another_course) is False


def test_true_if_course_is_attached(ten_percent_promocode, course):
    ten_percent_promocode.courses.add(course)

    assert ten_percent_promocode.compatible_with(course) is True
