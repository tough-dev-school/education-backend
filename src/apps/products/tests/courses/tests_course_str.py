import pytest

pytestmark = [pytest.mark.django_db]


def test_course_with_group(factory):
    group = factory.group(name="Милые котики")
    course_with_group = factory.course(name="Курс как стать милым котиком", group=group)
    assert str(course_with_group) == "Курс как стать милым котиком - Милые котики"
