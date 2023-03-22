import pytest

pytestmark = [pytest.mark.django_db]


def test_course(mixer):
    course = mixer.blend("products.Course", name="Курс как стать милым котиком")
    assert str(course) == "Курс как стать милым котиком"


def test_course_with_group(mixer):
    group = mixer.blend("products.Group", name="Милые котики")
    course_with_group = mixer.blend("products.Course", name="Курс как стать милым котиком", group=group)
    assert str(course_with_group) == "Курс как стать милым котиком - Милые котики"
